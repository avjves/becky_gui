import backups.databases.shelve_database as shelve_database
import backups.databases.exceptions as exceptions


def get_database(database_type, backup_model):
    """
    Returns a database model used to track the internal state of the
    backup model.
    """
    if database_type == 'shelve':
        return shelve_database.ShelveDatabase(backup_model)
    else:
        raise exceptions.DatabaseNotSupportedException(database_type)


