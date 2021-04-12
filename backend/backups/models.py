from django.db import models


class Backup(models.Model):
    name = models.CharField(max_length=128, null=False)
    provider = models.CharField(max_length=128, null=False)
    running = models.BooleanField(default=False)

    def to_simple_json(self):
        return {'id': self.id, 'name': self.name, 'provider': self.provider, 'running': self.running}

    def to_detailed_json(self):
        json_output = self.to_simple_json()
        for parameter in self.parameters.all():
            json_output[parameter.key] = parameter.value
        return json_output

    def get_backup_provider(self):
        return self.provider

    def get_provider_parameters(self):
        params = {}
        for parameter in self.parameters.all():
            params[parameter.key] = parameter.value
        return params



class BackupParameter(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE, related_name='parameters')
    key = models.CharField(max_length=64, null=False)
    value = models.CharField(max_length=1024, null=False)



