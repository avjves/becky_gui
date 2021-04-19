class CouldNotOpenDatabaseException(Exception):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Could not open database at path: {}".format(self.path)



class DatabaseNotOpenedException(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return "Database was not opened before attempting to retrieve  a key from it."



class KeyNotFoundException(Exception):

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Key {} does not exist in the database.".format(self.key)



class DatabaseInteractionException(Exception):

    def __init__(self, key, exception, message='Could not retrieve data with the given key.'):
        self.key = key
        self.message = message
        self.exception = exception

    def __str__(self):
        return "{} - Given key was: {} - Exception: {}".format(self.message, self.key, self.exception)


class DatabaseNotSupportedException(Exception):

    def __init__(self, database, message="Attempted to use an unsupported internal state database."):
        self.database = database
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- Database {} is not supported.".format(self.message, str(self.database))



