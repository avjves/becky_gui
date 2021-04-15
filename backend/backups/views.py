import json
import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View

from backups.models import Backup
from backups.backupper import Backupper
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
        for field in ['name', 'provider', 'path', 'running']:
            if field in backup_data:
                setattr(backup_model, field, backup_data[field])
                del backup_data[field]

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
        self._add_provider_specific_values(backup_model, backup_data)
        backup_model.save()
        return HttpResponse(status=200)




class BackupRunnerView(View):
    """ For now, the only way to start a backup process. """

    def get(self, request, backup_id):
        backup_model = Backup.objects.get(pk=backup_id)
        backupper =  Backupper(backup_model)
        backupper.backup()
        return HttpResponse(status=200)




class LogsView(View):
    """ In charge of returning any logs saved during the backup process. """

    def get(self, request, backup_id, **kwargs):
        current_page = int(request.GET.get('current_page'))
        rows_per_page = int(request.GET.get('rows_per_page'))

        backup_model = Backup.objects.get(pk=backup_id)
        logs = backup_model.log_rows.all().order_by('-timestamp')

        start_index = current_page*rows_per_page
        end_index = (current_page+1)*rows_per_page
        sliced_logs = logs[start_index:end_index]
        json_logs = [log.to_json() for log in sliced_logs]
        return JsonResponse({'logs': json_logs})


class FilesView(View):
    """ Allows the UI to query found files at a certain path. """

    def get(self, request, backup_id, **kwargs):
        path = request.GET.get('path')
        files = os.listdir(path)
        file_objects = [self._generate_file_object(path, f) for f in files]
        return JsonResponse({'files': file_objects})


    def _generate_file_object(self, path, filename):
        """
        Given a path, creates a file object.
        TODO: Check if said file is selected for backups.
        """
        print(path, filename)
        # name = filename.rsplit("/", 1)[-1
        name = filename
        # directory = path.rsplit(name, 1)[0]
        directory = path
        print(directory)
        if not directory: directory = '/'
        level = self._calculate_directory_level(os.path.join(path, filename))
        obj = {'filename': name, 'selected': False, 'directory': directory, 'level': level}
        if os.path.isdir(os.path.join(path, filename)):
            obj['file_type'] = 'directory'
            obj['files'] = []
        else:
            obj['file_type'] = 'file'
        return obj

    def _calculate_directory_level(self, path):
        """
        Given a path, calculates its level, i.e how many folders
        deep is it from the designed root level.
        TODO: Adhere to root setting.
        """
        root = "/"
        path = path.split(root, 1)[1]
        if not path: return 0
        level = len(path.split("/"))
        return level

