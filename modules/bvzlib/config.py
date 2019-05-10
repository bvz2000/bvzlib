import ConfigParser

import os


# ==============================================================================
class Config(ConfigParser.SafeConfigParser):
    """
    Class to manage configurations. Subclassed from the default python
    config parser.
    """

    # --------------------------------------------------------------------------
    def __init__(self, config_p=None, config_p_env_var=None):
        """
        Setup this subclass of the default python config parser.

        :param config_p: The path to the config file. If None OR
               config_p_env_var is not None and is valid, then the
               path will be taken from the config_p_env_var. Defaults to
               None.
        :param config_p_env_var: The env var that holds the path to the
               config file. If None, then resources_p must contain a value. If
               NOT None AND the env var exists AND it points to a file, then
               this path will be used instead of config_p. Defaults to None.

        :return: Nothing.
        """

        ConfigParser.SafeConfigParser.__init__(self, allow_no_value=True)

        assert not (config_p is None and config_p_env_var is None)

        if config_p_env_var is not None and config_p_env_var in os.environ:
            self.config_p = os.environ(config_p_env_var)
        else:
            self.config_p = config_p

        if not os.path.exists(self.config_p):
            raise IOError("Cannot locate config file: " + self.config_p)

        self.read(self.config_p)
