import json
import os
from tempfile import TemporaryDirectory
from django.test import TestCase
from backups.models import Backup
import backups.providers.tests.generic_tests as generic_tests

class S3ProviderTests(TestCase):
    def setUp(self):
        self.generic_tests = generic_tests.ProviderTests()
        pass

    def tearDown(self):
        pass

    def _get_s3_configs(self):
        try:
            config = {}
            home = os.path.expanduser('~')
            config_lines = open("{}/.s3cfg".format(home), "r").read().split('\n')
            for line in config_lines:
                splits = line.split("=")
                if len(splits) == 2:
                    config[splits[0].strip()] = splits[1].strip()
            return config
        except Exception as e:
            raise Exception('For S3 tests to work, there has to be a valid .s3cfg file in the root of the current user')

    def test_single_file(self):
        backup_model = Backup(name='_test_backup', provider='s3+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        config = self._get_s3_configs() 
        provider_settings = json.dumps({'access_key': config['access_key'], 'secret_key': config['secret_key'], 'host': config['host_base'], 'host_bucket': config['host_bucket'], 'bucket_name': config['bucket_name']})

        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_file(backup_model)
        backup_folder.cleanup()

    def test_single_differential_file(self):
        backup_model = Backup(name='_test_backup', provider='s3+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        config = self._get_s3_configs() 
        provider_settings = json.dumps({'access_key': config['access_key'], 'secret_key': config['secret_key'], 'host': config['host_base'], 'host_bucket': config['host_bucket'], 'bucket_name': config['bucket_name']})

        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_differential_file(backup_model)
        backup_folder.cleanup()

    def test_single_differential_file_wrong_timestamp(self):
        backup_model = Backup(name='_test_backup', provider='s3+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        config = self._get_s3_configs() 
        provider_settings = json.dumps({'access_key': config['access_key'], 'secret_key': config['secret_key'], 'host': config['host_base'], 'host_bucket': config['host_bucket'], 'bucket_name': config['bucket_name']})

        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_differential_file_wrong_timestamp(backup_model)
        backup_folder.cleanup()

    def test_single_folder(self):
        backup_model = Backup(name='_test_backup', provider='s3+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        config = self._get_s3_configs() 
        provider_settings = json.dumps({'access_key': config['access_key'], 'secret_key': config['secret_key'], 'host': config['host_base'], 'host_bucket': config['host_bucket'], 'bucket_name': config['bucket_name']})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_single_folder(backup_model)
        backup_folder.cleanup()

    def test_verify_files(self):
        backup_model = Backup(name='_test_backup', provider='s3+differential', scanner='local+differential', running=0)
        backup_model.save()
        backup_folder = TemporaryDirectory()
        config = self._get_s3_configs() 
        provider_settings = json.dumps({'access_key': config['access_key'], 'secret_key': config['secret_key'], 'host': config['host_base'], 'host_bucket': config['host_bucket'], 'bucket_name': config['bucket_name']})
        backup_model.add_parameter('providerSettings', provider_settings)
        self.generic_tests._test_backup_model_file_verification(backup_model)
        backup_folder.cleanup()


