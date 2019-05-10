class ErrorMsg(object):
    """
    An error object (simply holds error message and its error code).
    """

    def __init__(self):
        """
        setup
        """

        self._msg = ""
        self._code = 0

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, msg):
        assert type(msg) == str
        self._msg = msg

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        assert type(code) == int
        self._code = code

    # --------------------------------------------------------------------------
    def __str__(self):
        """
        Make the object behave like a string when printing, etc.

        :return: The string portion of the error message.
        """

        return self._msg
