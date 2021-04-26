import json
import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.base import View

from backups.models import Backup, BackupFile
from backups.backupper import Backupper
from becky.utils import join_file_path
from settings.models import GlobalParameter
from logs.models import BackupLogger


class BackupView(View):
    """ Handles showing, adding and editing the Backups and their parameters. """

    def get(self, request, **kwargs):
        if 'backup_id' in kwargs:
            return self._get_single_backup(request, kwargs.get('backup_id'))
        else:
            return self._list_backups(request)

    def post(self, request, backup_id):
        return self._add_backup(request, int(backup_id))

    def _add_backup(self, request, backup_id):
        """
        Adds a new one or edits an old backup model.
        """
        backup_data = json.loads(request.body)
        if backup_id == -1: # New Backup!
            backup = Backup()
            backup.save()
            fs_root = GlobalParameter.get_global_parameter(key='fs_root')
            backup.add_parameter(key='fs_root', value=fs_root)
        else:
            backup = Backup.objects.get(pk=backup_id)
        self._update_backup(request, backup, backup_data)
        return HttpResponse(status=200)

    def _add_global_values(self, backup_model, backup_data):
        """
        Adds 'global' values directly to the Backup model. 
        These are values that all Backup models have and are directly
        part of the model, instead of being a generic parameter value.
        """
        for field in ['name', 'provider', 'running']:
            if field in backup_data:
                setattr(backup_model, field, backup_data[field])
                del backup_data[field]


    def _add_files_to_backup(self, backup_model, backup_data):
        """
        Goes through all user provided selections and updates the files to backup 
        accordingly. User may send completely new selections or old ones that 
        turn off (i.e. delete a BackupFile model) a backup. 
        """
        for selection_path, selection_state in backup_data['selections'].items():
            if selection_state:
                backup_model.add_backup_file(selection_path)
            else:
                backup_model.delete_backup_file(selection_path)
        del backup_data['selections']


    def _add_provider_specific_values(self, backup_model, backup_data):
        """
        Adds provider specific / non-global values as BackupParameters.
        We assume that all global values have already been deleted from the
        backup_data dictionary.
        """
        for key, value in backup_data.items():
            param, created = backup_model.parameters.get_or_create(key=key)
            param.value = value
            param.save()

    def _get_single_backup(self, request, backup_id):
        """
        Returns all data from a single backup model.
        """
        backup = Backup.objects.get(pk=backup_id)
        return JsonResponse({'backup': backup.to_detailed_json()})

    def _list_backups(self, request):
        """
        Returns all Backups as a list of dictionaries.
        Here we only return their simple JSON representation.
        That is, we only return name, is_running and the provider name.
        """
        backups = [backup.to_simple_json() for backup in Backup.objects.all()]
        return JsonResponse({'backups': backups})

    def _update_backup(self, request, backup_model, backup_data):
        """
        Updates the given backup model with the new data.
        """
        del backup_data['id'] # Let's not even attempt to change Django IDs
        self._add_global_values(backup_model, backup_data)
        self._add_files_to_backup(backup_model, backup_data)
        self._add_provider_specific_values(backup_model, backup_data)
        backup_model.save()
        return HttpResponse(status=200)

    def _get_user_root(self, backup_model):
        """
        Queries for the user root, if it hasn't already been queried.
        Saves the user root to this class, so other funcions can access it as well.
        """
        return backup_model.get_user_root()
        # if backup_model and backup_model.pk:
            # self.user_root = backup_model.get_parameter('fs_root').value
        # else:
            # self.user_root = GlobalParameter.get_global_parameter(key='fs_root')
        # return self.user_root


class DeleteView(View):
    """ Simple view to used to delete a backup. """

    def post(self, request, backup_id):
        backup_model = Backup.objects.get(pk=backup_id)
        backup_model.delete()
        return HttpResponse(status=200)


class BackupRunnerView(View):
    """ For now, the only way to start a backup process. """

    def get(self, request, backup_id):
        backup_model = Backup.objects.get(pk=backup_id)
        backupper =  Backupper(backup_model)
        try:
            backupper.backup()
        except Exception as e:
            backup_model.set_status('Idle due to an error')
            raise e
        return HttpResponse(status=200)




class LogsView(View):
    """ In charge of returning any logs saved during the backup process. """

    def get(self, request, backup_id, **kwargs):
        current_page = int(request.GET.get('current_page'))
        rows_per_page = int(request.GET.get('rows_per_page'))
        levels_to_show = json.loads(request.GET.get('levels_to_show'))
        levels_to_show = [key.upper() for key, value in levels_to_show.items() if value == True]
        if levels_to_show:
            backup_model = Backup.objects.get(pk=backup_id)
            q = Q()
            for level_to_show in levels_to_show:
                q.add(Q(level=level_to_show), Q.OR)
            logs = backup_model.log_rows.filter(q).order_by('-timestamp')

            start_index = current_page*rows_per_page
            end_index = (current_page+1)*rows_per_page
            sliced_logs = logs[start_index:end_index]
            json_logs = [log.to_json() for log in sliced_logs]
        else:
            json_logs = []
        return JsonResponse({'logs': json_logs})


class FilesView(View):
    """ Allows the UI to query found files at a certain path. Automatically adds the user defined root to all requests. """

    def get(self, request, backup_id, **kwargs):
        path = request.GET.get('path')
        backup_model = self._get_backup_model(backup_id)
        #self._get_user_root(backup_model) # Save backup_id to the model once, so we don't have to pass it around to all functions
        files_path = self._ensure_default_directory_level(path, backup_model)
        files = os.listdir(files_path)
        file_objects = [self._generate_file_object(path, f, backup_model) for f in files]
        return JsonResponse({'files': file_objects})

    def _get_backup_model(self, backup_id):
        """
        Returns a backup model for the current backup ID.
        If backup_id is -1 ( adding a new Backup model, not yet saved),
        we create a temporary model that won't be saved.
        Otherwise, we just fetch actual model.
        """
        if backup_id == '-1':
            return Backup() 
        else:
            return Backup.objects.get(pk=backup_id)


    def _generate_file_object(self, directory, filename, backup_model):
        """
        Given a path, creates a file object.
        TODO: Check if said file is selected for backups.
        """
        level = self._calculate_directory_level(join_file_path(directory, filename))
        obj = {'filename': filename, 'selected': False, 'directory': directory, 'level': level}
        obj['selected'] = self._check_file_selection(directory, filename, backup_model)
        if self._path_is_directory(directory, filename, backup_model):
            obj['file_type'] = 'directory'
            obj['files'] = []
        else:
            obj['file_type'] = 'file'
        return obj

    def _calculate_directory_level(self, path):
        """
        Given a path, calculates its level, i.e how many folders
        deep is it from the designed root level.
        """
        root = "/"
        path = path.split(root, 1)[1]
        if not path: return 0
        level = len(path.split("/"))
        return level

    def _check_file_selection(self, directory, filename, backup_model):
        """
        Checks whether the given file/folder in the given directory has been saved
        for backing up.
        """
        path = join_file_path(backup_model.get_user_root(), directory, filename)
        backup_file = backup_model.get_backup_file(path)
        if backup_file:
            return True
        else:
            return False

    def _ensure_default_directory_level(self, path, backup_model):
        """
        Ensures that the default path set by the user is
        at the beginning of the path.
        """
        user_root = backup_model.get_user_root()
        if not path.startswith(user_root):
            path = os.path.join(user_root, path.strip("/"))
        return path

    def _path_is_directory(self, directory, filename, backup_model):
        """
        Checks whether the given file in in the given directory
        is a directory. Adds the user defined root to the front.
        """
        if os.path.isdir(join_file_path(backup_model.get_user_root(), directory, filename)):
            return True
        else:
            return False

    def _get_user_root(self, backup_model):
        """
        Queries for the user root, if it hasn't already been queried.
        Saves the user root to this class, so other funcions can access it as well.
        """
        return backup_model.get_user_root()
        if backup_model and backup_model.pk:
            self.user_root = backup_model.get_parameter('fs_root').value
        else:
            self.user_root = GlobalParameter.get_global_parameter(key='fs_root')
        return self.user_root

class RestoreFilesView(FilesView):

    def get(self, request, backup_id, **kwargs):
        path = request.GET.get('path')
        backup_model = self._get_backup_model(backup_id)
        self._get_user_root(backup_model) # Save backup_id to the model once, so we don't have to pass it around to all functions
        provider = backup_model.get_backup_provider()
        files = provider.get_remote_files(path)
        file_objects = [self._generate_file_object(path, f, backup_model) for f in files]
        return JsonResponse({'files': file_objects})

    def post(self, request, backup_id, **kwargs):
        data = json.loads(request.body)
        selections = data['selections']
        selections = list(selections.keys())
        restore_path = data['restore_path']
        backup_model = self._get_backup_model(backup_id)
        backup_model.restore_files(selections, restore_path)
        return HttpResponse(status=200)


    def _check_file_selection(self, directory, filename, backup_model):
        """
        Nothing should ever be checked by default during the restore process, so always return False here.
        """
        return False

