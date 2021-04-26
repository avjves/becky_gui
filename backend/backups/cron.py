from backup.model import Backup
def run_periodic_backups():
    """
    Function called every minute by the django-crontab.
    Checks if there is any backups that should be ran and starts running them.
    """
    for backup_model in Backup.objects.filter(running=1):
        backup_model.run_backup()
