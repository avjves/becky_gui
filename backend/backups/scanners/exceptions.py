class ScannerNotSupportedException(Exception):

    def __init__(self, scanner, message="Attempted to use an unsupported file scanner."):
        self.scanner = scanner
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- File scanner {} is not supported.".format(self.message, str(self.scanner))



