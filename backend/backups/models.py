import json
import os
import pathlib
import datetime
import hashlib
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist

import backups.providers as providers
import backups.scanners as scanners
from settings.models import GlobalParameter
from logs.models import BackupLogger
from becky.utils import remove_prefix

class Backup(models.Model):
    name = models.CharField(max_length=128, null=False)
    scanner = models.CharField(max_length=128, null=False)
    provider = models.CharField(max_length=128, null=False)
    running = models.BooleanField(default=False)

    def to_simple_json(self):
        return {'id': self.id, 'name': self.name, 'scanner': self.scanner, 'provider': self.provider, 'running': self.running}

    def to_detailed_json(self):
        json_output = self.to_simple_json()
        json_output.update(self.get_provider_parameters())
        file_selections = {}
        for backup_file in self.files.all():
            file_selections[backup_file.path] = True
        size_in_bytes = 0
        with transaction.atomic():
            for backup_item in self.backup_items.all():
                size_in_bytes += backup_item.file_size
        json_output['total_size'] = round(size_in_bytes / 1024 / 1024, 2) #Size in MB
        json_output['selections'] = file_selections

        return json_output

    def create_backup_file_instance(self, path):
        """
        Given a file path, creates BackupFiles from it if one doesn't already exist in the database.
        This is a helper function for scanners/providers, so that they can easily
        generate new BackupFile objects at any point. 
        """
        backup_file = BackupItem(backup=self, path=path)
        backup_file.update_metadata()
        return backup_file

    def create_backup_file_instances(self, files):
        """
        Calls 'create_backup_file_instances' for each file given in
        and returns the values as a list.
        """
        backup_files = [self.create_backup_file_instance(f) for f in files]
        return backup_files

    def get_remote_files(self, path):
        """
        Retrieves all saved Backup Items in the current path.
        """
        files = BackupItem.objects.filter(directory=path)
        return files


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
        scanner = scanners.get_scanner(self.scanner, self)
        return scanner

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
        return backup_file

    def delete_backup_file(self, path):
        """
        Attempts to delete a backup file with the given path.
        If none such exists, we just return.
        """
        try:
            bf = self.files.get(path=path)
            bf.delete()
        except ObjectDoesNotExist:
            pass

    def get_all_backup_items(self):
        backup_items = self.backup_items.all()
        return backup_items

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
        found_files = scanner.scan_files(self.get_all_backup_files())
        logger.log("Starting file backing...", 'BACKUP', 'INFO')
        # self.set_status('Backing up files...')
        saved_files = provider.backup_files(found_files)
        with transaction.atomic():
            for f in saved_files:
                f.calculate_checksum()
                f.save()
        logger.log("Backup done.", 'BACKUP', 'INFO')
        self.set_status('Idle', 0, 0)

    def verify_files(self):
        """
        Runs a verify action on the provider.
        This checks if the local and remote data are in sync by comparing their hashes.
        """
        provider = self.get_backup_provider()
        logger = self._get_logger()
        logger.log("Starting backup verification process.", 'BACKUP', 'INFO')
        provider.verify_files()
        logger.log("Files verified successfully.", 'BACKUP', 'INFO')

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
        

class BackupItem(models.Model):
    path = models.TextField(null=False)
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='backup_items')
    filename = models.TextField()
    directory = models.TextField()
    file_size = models.BigIntegerField(default=0)
    modified = models.TimeField(null=True)
    checksum = models.CharField(max_length=64)

    def calculate_checksum(self):
        """
        Calculates a MD5 checksum hash of the current file.
        This is used to verify that the content match.
        """
        if os.path.isdir(self.path):
            self.checksum = '0'
        else:
            content = open(self.path, 'rb').read()
            checksum = hashlib.md5()
            checksum.update(content)
            self.checksum = checksum.hexdigest()
        

    def update_metadata(self):
        self._set_path_metadata()
        self._set_file_metadata()

    def _set_file_metadata(self):
        """
        Updates the file metadata if possible, such as 
        file size.
        TODO: other metadata, like modified timestamps etc.
        """
        if os.path.exists(self.path):
            if os.path.isdir(self.path):
                self.file_size = 0 #For now
            else:
                self.file_size = os.path.getsize(self.path)

            modified = int(pathlib.Path(self.path).stat().st_mtime)
            self.modified = datetime.datetime.fromtimestamp(modified)


    def _set_path_metadata(self):
        """
        Sets the directory field to be the folder where the given item exists.
        If the path is just root, directory is set to None.
        """
        if self.path == '/':
            self.filename = '/'
            self.directory = ''
        else:
            splits = self.path.rsplit('/', 1)
            folder = splits[0] if splits[0] else '/'
            filename = splits[1]
            self.directory = folder
            self.filename = filename


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

