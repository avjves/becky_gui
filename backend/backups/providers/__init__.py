from backups.providers.local_provider import LocalProvider
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
    else:
        raise exceptions.ProviderNotSupportedException(provider_name)
