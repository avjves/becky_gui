import json
import os
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist

import backups.providers as providers
import backups.scanners as scanners
import backups.databases as databases
from settings.models import GlobalParameter
from logs.models import BackupLogger
from becky.utils import remove_prefix

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

    def create_backup_file_instance(self, path):
        """
        Given a file path, creates BackupFiles from it.
        This is a helper function for scanners/providers, so that they can easily
        generate new BackupFile objects at any point. 
        """
        backup_file = BackupFile(backup=self, path=path)
        return backup_file

    def create_backup_file_instances(self, files):
        """
        Calls 'create_backup_file_instances' for each file given in
        and returns the values as a list.
        """
        backup_files = [self.create_backup_file_instance(f) for f in files]
        return backup_files

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
        try:
            parameter = self.parameters.get(key=key)
        except ObjectDoesNotExist:
            parameter = GlobalParameter.get_global_parameter(key)
        return parameter

    
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

    def add_backup_file(self, path):
        """
        Creates a BackupFile from the given path.
        If an BackupFile tied to this model already exists
        with the given path, nothing is changed.
        """
        backup_file, _ = self.files.get_or_create(backup=self, path=path)
        backup_file.save()

    def delete_backup_file(self, path):
        """
        Attempts to delete a backup file with the given path.
        If none such exists, we just return.
        """
        try:
            bf = self.files.objects.get(path=path)
            bf.delete()
        except ObjectDoesNotExist:
            pass

    def get_all_backup_files(self):
        """
        Returns all backup file paths tied to this model as a list.
        """
        backup_files = self.files.all()
        return backup_files

    def get_status(self):
        """
        Returns the current status of the backup model.
        Returns the current status message and the current percentage of
        the task at hand.
        """
        if self.statuses.exists():
            return self.statuses.first().to_json()
        else:
            return {'status_message': 'Idle', 'percentage': '100', 'running': 0}

    def is_running(self):
        """
        Returns whether the current backup model is in middle of a 
        backup.
        """
        if self.get_status()['running'] == 'Idle':
            return False
        else:
            return True

    def restore_files(self, selections, restore_path):
        """
        Sends the selections and restore path to this backup model's 
        BackupProvider that will then restore the selected files to
        the restore_path folder.
        """
        selections = self.create_backup_file_instances(selections)
        provider = self.get_backup_provider()
        provider.restore_files(selections, restore_path)

    def run_backup(self):
        """
        Starts the backup process. If this is the first time running it,
        it first generates the database and then backups everything.
        On subsequent runs it just scans for new/changed files and backups those.
        """
        scanner = self.get_file_scanner()
        provider = self.get_backup_provider()
        logger = self._get_logger()
        logger.log("Starting file scanning...", 'BACKUP', 'INFO')
        # self.set_status('Scanning for files...')
        scanner.scan_files(self.get_all_backup_files())
        logger.log("Starting file backing...", 'BACKUP', 'INFO')
        # self.set_status('Backing up files...')
        provider.backup_files(scanner.get_changed_files())
        logger.log("Starting file marking...", 'BACKUP', 'INFO')
        scanner.mark_new_files()
        self.set_status('Idle', 0, 0)

    def set_status(self, status_message, percentage, running):
        """
        Sets the current status of the backup model to the given status.
        """
        with transaction.atomic():
            new_status = BackupStatus(backup=self, message=status_message, percentage=percentage, running=running)
            self.statuses.all().delete()
            new_status.save()

    def _get_logger(self):
        """
        Returns a logger object that other objects can and will use to log their events.
        TODO: For now, just using the default logger. At someone allow using different loggers as well?
        """
        logger = BackupLogger(self)
        return logger

    

class BackupFile(models.Model):
    path = models.TextField(null=False)
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='files')

    def to_json(self):
        return {'path': self.path}
        

class BackupStatus(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='statuses')
    message = models.TextField()
    percentage = models.IntegerField()
    running = models.BooleanField()

    def to_json(self):
        return {'status_message': self.message, 'percentage': self.percentage, 'running': self.running}

class BackupParameter(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='parameters')
    key = models.CharField(max_length=64, null=False)
    value = models.CharField(max_length=1024, null=False)

