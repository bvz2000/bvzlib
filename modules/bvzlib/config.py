"""
License
--------------------------------------------------------------------------------
bvzlib is released under version 3 of the GNU General Public License.

bvzlib
Copyright (C) 2019  Bernhard VonZastrow

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
            self.config_p = os.environ[config_p_env_var]
        else:
            self.config_p = config_p

        if not os.path.exists(self.config_p):
            raise IOError("Cannot locate config file: " + self.config_p)

        self.read(self.config_p)

    # --------------------------------------------------------------------------
    def save(self):
        """
        Writes the config parser back out to disk.

        :return: Nothing.
        """

        with open(self.config_p, "w") as f:
            self.write(f)