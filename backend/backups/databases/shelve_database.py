import shelve
import os

from backups.databases.base_database import BaseDatabase
import backups.databases.exceptions as exceptions


class ShelveDatabase(BaseDatabase):
    """ 
    Database that uses a simple Shelve. Note: This is for saving the internal state
    of a single backup model, such as scanned files, backed up files etc.
    """

    def __init__(self, backup):
        self.backup_name = backup.name
        self.db_loc = '{}.shelve'.format(os.path.join("/home/avjves/dbs", self.backup_name))


    def open_connection(self, state_name):
        """
        Opens a shelve connection.
        If the connection opening worked,
        returns True, else raises an exception.
        """
        try:
            self.db = shelve.open(self.db_loc)
            self.state_name = state_name
            if not self.state_name in self.db:
                self.db[self.state_name] = {}
            return True
        except:
            raise exceptions.CouldNotOpenDatabaseException(self.db_loc)
    
    def close_connection(self):
        """
        Closes the connection to the shelve database if said
        connection exists.
        """
        if hasattr(self, 'db'):
            self.db.close()
            delattr(self, 'db')
            delattr(self, 'state_name')


    def get(self, key, default_value=None):
        """
        Retrieves data from the database with the given key.
        If it doesn't exist, throws an exception, unless a default value has been specified.
        """
        if not hasattr(self, 'db'):
            raise exceptions.DatabaseNotOpenedException
        if key not in self.db[self.state_name] and default_value != None:
            return default_value
        if key not in self.db[self.state_name]:
            raise exceptions.KeyNotFoundException(key)
        try:
            data = self.db[self.state_name].get(key)
            return data
        except Exception as e:
            raise exceptions.DatabaseInteractionException(key=key, message='Could not retrieve data with the given key.', exception=e)

    def save(self, key, value):
        """
        Saves value to the DB with the given key.
        Any data currently saved under the key will be overwritten.
        """ 
        if not hasattr(self, 'db'):
            raise exceptions.DatabaseNotOpenedException

        try:
            state_data = self.db[self.state_name]
            state_data[key] = value
            self.db[self.state_name] = state_data
        except Exception as e:
            raise exceptions.DatabaseInteractionException(key=key, message='Could not save data with the given key.', exception=e)


    def clear(self):
        """
        Completely clears the state data from the current database.
        """
        if not hasattr(self, 'db'):
            raise exceptions.DatabaseNotOpenedException

        try:
            self.db[self.state_name] = {}
        except Exception as e:
            raise exceptions.DatabaseInteractionException(key=key, message='Could not save data with the given key.', exception=e)

