from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class GlobalParameter(models.Model):
    key = models.CharField(max_length=128, null=False)
    value = models.CharField(max_length=128, null=False)

    supported_parameters = ['fs_root', 'test_setting']

    @classmethod
    def get_all_global_parameters(cls):
        """
        Returns all global parameters as a dictionary.
        """
        params = {}
        for key in cls.supported_parameters:
            params[key] = GlobalParameter.get_global_parameter(key=key)
        return params


    @staticmethod
    def get_global_parameter(key):
        """
        Returns a single global parameter value.
        We use this staticmethod instead of directly
        querying the DB for one so that we can easily
        set a default value for a key that might not exist yet.
        """
        try:
            param = GlobalParameter.objects.get(key=key)
            return param
        except ObjectDoesNotExist:
            return ''

    @classmethod
    def save_parameter(cls, key, value):
        """
        Saves a new parameter with the given key and value.
        If said key already exists, overwrites it.
        Also checks whether the key is valid, i.e. do we have
        a default value for it. If not, throws an exception.
        """
        if key in cls.supported_parameters:
            param, _ = GlobalParameter.objects.get_or_create(key=key)
            param.value = value
            param.save()
        else:
            raise IllegalParameterException(key)
         


    def to_json(self):
        return {'id': self.id, 'key': self.key, 'value': self.value}


class IllegalParameterException(Exception):

    def __init__(self, key, message="Attempted to save an illegal parameter."):
        self.key = key
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- Parameter {} is not supported.".format(self.message, str(self.key))








