class UserPub:
    """
    The class Used to publish interim result to user client. It must be the second param of run method.
    The only method of this class is 'publish' which used to publish interim result.

    Usage: userpub.pulish(message)
    """
    def publish(self, message: bytes):
        """Publish message to client.

        arg message must be bytes type, so you should convert your data to bytes before publish it. Or it will raise exception and the job will fail.

        Args:
            message: Msg user want to publish when running.


        """
        pass