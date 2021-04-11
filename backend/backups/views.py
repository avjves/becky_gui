import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View

from backups.models import Backup



class BackupView(LoginRequiredMixin, View):

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

