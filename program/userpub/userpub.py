class UserPub:
    """
    The class Used to publish interim result to user client. It must be the second param of run method.
    The only method of this class is 'publish' which used to publish interim result.

    Usage: userpub.pulish(message)
    """
    def publish(self, message: bytes):
        """
        It only receives message(type of bytes).
        So you should change your data to bytes before publish it. Or it will raise exception and the job will fail.
        """
        pass