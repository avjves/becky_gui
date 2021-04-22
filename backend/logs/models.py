from django.db import models

from backy.utils import format_timestamp_gui


class LogRow(models.Model):
    backup = models.ForeignKey('backups.Backup', on_delete=models.CASCADE, related_name='log_rows')
    level = models.CharField(max_length=32, null=False)
    tag = models.CharField(max_length=32, null=False)
    message = models.CharField(max_length=512, null=False)
    timestamp = models.DateTimeField(auto_now=True)

    def to_json(self):
        return {'backup_id': self.backup.id, 'level': self.level, 'tag': self.tag, 'message': self.message, 'timestamp': format_timestamp_gui(self.timestamp)}



"""
Backupper that any scanner or provider can use to add logs to specific backup model.
"""
class BackupLogger:

    def __init__(self, backup_model):
        self.backup_model = backup_model

    def log(self, message, tag, level):
        """
        Adds a single row level log with the supplied message. Tag and the level are applied to log.
        """
        self._check_level_validity(level)
        self._add_log_row(message, tag, level)
        self._print_log(message, tag, level)

    def _add_log_row(self, message, tag, level):
        """
        Creates a new LogRow object and saves it to the DB.
        """
        try:
            log_model = LogRow(backup=self.backup_model, level=level, tag=tag, message=message)
            log_model.save()
        except Exception as e:
            raise FailedToLogException(e)

    def _check_level_validity(self, level):
        """
        Checks whether the given 'level' is valid.
        If not, throws an error.
        """
        allowed_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        if level not in allowed_levels:
            raise InvalidLogLevelException(level)

    def _print_log(self, message, tag, level):
        """
        Debug function to print all logs to terminal
        """
        print('{} - {}: {}'.format(tag, level, message))

    

class InvalidLogLevelException(Exception):
    """ Exception thrown when user attempts to save a log with improper log level """

    def __init__(self, level, message="Supplied log level not a valid log level. Valid levels are INFO, WARNING, ERROR and DEBUG."):
        self.level = level
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "Level: {} -- {}".format(self.level, self.message)


class FailedToLogException(Exception):
    """ Generic 'failed to log' exception. Raised when something unexpected went wrong saving the log row. """

    def __init__(self, exception, message="Ran into a problem while saving a log row."):
        self.exception = exception
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- Exception message: {}".format(self.message, str(self.exception))

