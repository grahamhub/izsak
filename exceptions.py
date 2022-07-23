class NotFound(Exception):
    """For when a resource is not found."""
    def __init__(self, msg):
        super().__init__(msg)