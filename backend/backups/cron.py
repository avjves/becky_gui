from django.utils import timezone
from backups.models import Backup

def run_periodic_backups():
    """
    Function called every minute by the django-crontab.
    Checks if there is any backups that should be ran and starts running them.
    """
    print("Starting periodic backups")
    for backup_model in Backup.objects.filter(running=1):
        current_time = timezone.now().timestamp()
        should_run = backup_model.should_run_now(current_time)
        if should_run:
            print("Running backup model", backup_model.name, timezone.now().strftime("%d/%m/%Y %H:%M:%S"))
            backup_model.run_backup()



