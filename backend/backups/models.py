from django.db import models
from django.core.exceptions import ObjectDoesNotExist


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
        return self.provider

    def get_provider_parameters(self):
        params = {}
        for parameter in self.parameters.all():
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
        backup_files = [bf.path for bf in backup_files]
        return backup_files


class BackupFile(models.Model):
    path = models.TextField(null=False)
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='files')


class BackupParameter(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='parameters')
    key = models.CharField(max_length=64, null=False)
    value = models.CharField(max_length=1024, null=False)



