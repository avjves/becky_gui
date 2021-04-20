import json
import os
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import backups.providers as providers
import backups.scanners as scanners
import backups.databases as databases
from settings.models import GlobalParameter
from logs.models import BackupLogger
from backy.utils import remove_prefix

class Backup(models.Model):
    name = models.CharField(max_length=128, null=False)
    provider = models.CharField(max_length=128, null=False)
    running = models.BooleanField(default=False)

    def to_simple_json(self):
        return {'id': self.id, 'name': self.name, 'provider': self.provider, 'running': self.running}

    def to_detailed_json(self):
        json_output = self.to_simple_json()
        json_output.update(self.get_provider_parameters())
        file_selections = {}
        for backup_file in self.files.all():
            file_selections[backup_file.path] = True
        json_output['selections'] = file_selections

        return json_output

    def get_backup_provider(self):
        """
        Checks the desired backup provider from the model and intializes a proper 
        backup provider model.
        """
        provider = providers.get_provider(self.provider, self)
        return provider

    def get_file_scanner(self):
        """
        Checks the desired file scanner from the model and intializes it.
        """
        scanner = scanners.get_scanner('local', self)
        return scanner

    def get_state_database(self):
        """
        Returns a database that reflects the internal state of this backup model.
        """
        state_database = databases.get_database('shelve', self)
        return state_database

    def get_provider_parameters(self):
        params = {}
        for parameter in self.parameters.all():
            try:
                params[parameter.key] = json.loads(parameter.value) # Can be anything, so saved to DB as a JSON string
            except json.JSONDecodeError:
                params[parameter.key] = parameter.value
        return params

    def add_parameter(self, key, value, allow_duplicate=False):
        """
        Adds a BackupParameter to the current model.
        If allow_duplicate is False, any existing parameter with
        the same key will be overwritten.
        """
        if allow_duplicate:
            param, _ = BackupParameter.objects.get_or_create(backup=self, key=key, value=value)
        else:
            params = BackupParameter.objects.filter(backup=self, key=key)
            params.delete()
            param = BackupParameter(backup=self, key=key, value=value)
        param.save()

    def get_parameter(self, key):
        """
        Returns a BackupParameter model with the given key that is tied to this Backup.
        """
        parameter = self.parameters.get(key=key)
        return parameter

    def get_user_root(self):
        """
        Returns the user defined root for this backup model.
        If none has been set yet, returns the global default value.
        """
        try:
            return self.get_parameter('fs_root').value
        except ObjectDoesNotExist:
            return GlobalParameter.get_global_parameter('fs_root')

    def get_backup_file(self, path):
        """
        Checks whether the backup contains a file with the given path.
        Returns a BackupFile object if it exists, otherwise None.
        """
        try:
            backup_file = self.files.get(path=path)
            return backup_file
        except ObjectDoesNotExist:
            return None

    def get_all_backup_files(self):
        """
        Returns all backup file paths tied to this model as a list.
        """
        backup_files = self.files.all()
        return backup_files

    def restore_files(self, selections, restore_path):
        """
        Sends the selections and restore path to this backup model's 
        BackupProvider that will then restore the selected files to
        the restore_path folder.
        """
        selections = self._expand_selections(selections)
        provider = self.get_backup_provider()
        provider.restore_files(selections, restore_path)

    def _get_logger(self):
        """
        Returns a logger object that other objects can and will use to log their events.
        TODO: For now, just using the default logger. At someone allow using different loggers as well?
        """
        logger = BackupLogger(self)
        return logger

    def _expand_selections(self, selections):
        """
        Expands a list of relative paths into the BackupFile JSON format with proper paths.
        """
        expanded_selections = []
        user_root = self.get_user_root()
        for selection in selections:
            expanded = {'path': os.path.join(user_root, remove_prefix(selection, '/')), 'relative_path': selection}
            expanded_selections.append(expanded)
        return expanded_selections



class BackupFile(models.Model):
    path = models.TextField(null=False)
    relative_path = models.TextField(null=False)
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='files')

    def get_root(self):
        """
        Returns the root of the path that we don't want to backup.
        I.e, the difference between path and relative_path.
        TODO: FIX
        """
        return self.path[:-len(self.relative_path)]

    def to_json(self):
        return {'path': self.path, 'relative_path': self.relative_path}
        


class BackupParameter(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='parameters')
    key = models.CharField(max_length=64, null=False)
    value = models.CharField(max_length=1024, null=False)



