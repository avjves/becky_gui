import backups.scanners.local_scanner as local_scanner
import backups.scanners.exceptions as exceptions


def get_scanner(scanner_name, backup_model):
    """
    Returns a scanner with the given scanner name.
    """
    parameters = backup_model.get_provider_parameters()
    if scanner_name == 'local':
        scanner = local_scanner.LocalFilesScanner(parameters, backup_model)
    else:
        raise exceptions.ScannerNotSupportedException(scanner_name)
    return scanner

