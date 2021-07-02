
class ApplicationException(Exception):
    """Custom Exception for Application"""
    def __init__(self,message, errors):
        super().__init__(message)
        self.e = errors