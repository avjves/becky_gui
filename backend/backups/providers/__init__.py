from backups.providers.local_provider import LocalProvider
from backups.providers.differential_local_provider import DifferentialLocalProvider
from backups.providers.differential_remote_provider import DifferentialRemoteProvider
from backups.providers.differential_s3_provider import DifferentialS3Provider
from backups.providers.remote_provider import RemoteProvider
from backups.providers.s3_provider import S3Provider
import backups.providers.exceptions as exceptions


def get_provider(provider_name, backup_model):
    """
    Returns a BackupProvider that matches the given name.
    Supplies the given parameters and the current Backup model
    to it.
    """
    parameters = backup_model.get_provider_parameters()

    if provider_name == 'local':
        return LocalProvider(parameters, backup_model)
    elif provider_name == 'local+differential':
        return DifferentialLocalProvider(parameters, backup_model)
    elif provider_name == 'remote+differential':
        return DifferentialRemoteProvider(parameters, backup_model)
    elif provider_name == 's3+differential':
        return DifferentialS3Provider(parameters, backup_model)
    elif provider_name == 'remote':
        return RemoteProvider(parameters, backup_model)
    elif provider_name == 's3':
        return S3Provider(parameters, backup_model)
    else:
        raise exceptions.ProviderNotSupportedException(provider_name)
