class  ProviderNotSupportedException(Exception):
    def __init__(self, provider, message="Attempted to use an unsupported provider."):
        self.provider = provider
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "{} -- Provider {} is not supported.".format(self.message, str(self.provider))



