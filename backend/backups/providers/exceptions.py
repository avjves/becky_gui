class ProviderNotSupportedException(Exception):
    def __init__(self, provider, message="Attempted to use an unsupported provider."):
        self.provider = provider
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- Provider {} is not supported.".format(self.message, str(self.provider))


class DataVerificationFailedException(Exception):

    def __init__(self, fail_count, message="Data verification failed."):
        self.fail_count = fail_count
        self.message = message

    def __str__(self):
        return "{} -- {} files failed.".format(self.message, self.fail_count)
        
