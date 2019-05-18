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

import argparse
import ConfigParser
import os
import inspect

from bvzlib import resources

# define some colors
# ------------------------------------------------------------------------------
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
BRIGHT_WHITE = '\033[97m'
ENDC = '\033[0m'


class Options(object):
    """
    Wrapper for the arg parser object.
    """

    def __init__(self, options_list, resc, argv, language="english"):
        """
        Setup.

        :param options_list: A list of option names to read from the resources
               file.
        :param argv: The full sys.argv list.
        :param resc: The resources file that contains the options.
        :param language: The language to use for the resources file.

        :return: Nothing.
        """

        module_d = os.path.split(inspect.stack()[0][1])[0]
        resources_d = os.path.join(module_d, "..", "..", "resources")
        self.local_resc = resources.Resources(resources_d, "options", language)

        self.resc = resc
        self.options_list = options_list
        self.argv = argv

        self.opts, self.args = self.define_options()

    # ------------------------------------------------------------------------------
    def define_options(self):
        """
        Sets up the option parser.

        :return: A tuple where the first item is a fully populated option parser
                 object, and the second is a list of the remaining arguments.
        """

        # set up the parser
        description = self.resc.items("description")
        description = self.format_multi_line(description)

        usage = self.resc.items("usage")
        usage = self.format_multi_line(usage)

        parser = argparse.ArgumentParser(description=description, usage=usage)

        # Set up each option
        for option_name in self.options_list:

            option_name = "options-" + option_name

            if not self.resc.has_section(option_name):
                err = self.local_resc.error(106)
                err.msg = err.msg.format(path=self.resc.resources_p,
                                         section=option_name)
                raise ValueError(err.msg)

            if not self.resc.has_option(option_name, "meta_var"):
                self.resc.set(option_name, "meta_var",
                              "{{COLOR_RED}}No Meta Var{{COLOR_NONE}}")

            if not self.resc.has_option(option_name, "description"):
                self.resc.set(option_name, "description",
                              "{{COLOR_RED}}No Desc. Available{{COLOR_NONE}}")

            flags = [
                "short_flag",
                "long_flag",
                "action",
                "dest",
                "default",
                "type",
                "metavar",
                "nargs",
                "required",
                "description",
            ]

            settings = dict()

            for flag in flags:
                try:
                    settings[flag] = self.resc.get(option_name, flag)
                except ConfigParser.NoOptionError:
                    err = self.local_resc.error(107)
                    err.msg = err.msg.format(path=self.resc.resources_p,
                                             section=option_name,
                                             setting=flag)
                    raise ValueError(err.msg)

            arg_list, arg_dict = self.format_for_argparse(settings)
            parser.add_argument(*arg_list, **arg_dict)

        # actually parse the command my_line
        opts, args = parser.parse_known_args(self.argv)

        return opts, args

    # --------------------------------------------------------------------------
    @staticmethod
    def format_for_argparse(settings):
        """
        Build the argparser args. This is required because argparse contains a
        whole slew of incompatible arguments.

        :return: A tuple: the first element is a list and the second a dict.
        """

        lst = list()
        dct = dict()

        # Short Flag
        if settings["short_flag"]:
            lst.append(settings["short_flag"])

        # Long Flag
        if settings["long_flag"]:
            lst.append(settings["long_flag"])

        # Action
        if settings["action"]:
            dct["action"] = settings["action"]
        else:
            dct["action"] = None

        # Dest
        if settings["dest"]:
            dct["dest"] = settings["dest"]

        # Default
        if settings["default"]:
            # Boolean
            if settings["type"].lower() == "bool":
                if settings["default"].lower() == "true":
                    dct["default"] = True
                else:
                    dct["default"] = False
            # Integer
            elif settings["type"].lower() == "int":
                dct["default"] = int(settings["default"])
            # String
            else:
                dct["default"] = settings["default"]
        else:
            dct["default"] = ""

        # Type
        if settings["type"]:
            if settings["type"] == "str":
                dct["type"] = str
            if settings["type"] == "list":
                dct["type"] = list
        else:
            dct["type"] = None

        # Metavar
        if settings["metavar"]:
            dct["metavar"] = tuple(settings["metavar"].split(","))

        # Nargs
        if settings["nargs"]:
            if settings["nargs"] in ["?", "*", "+"]:
                dct["nargs"] = settings["nargs"]
            else:
                try:
                    nargs = int(settings["nargs"])
                except ValueError:
                    nargs = 0
                if nargs >= 2:
                    try:
                        dct["nargs"] = int(settings["nargs"])
                    except ValueError:
                        pass

        # Required
        if settings["required"]:
            if settings["required"].upper() == "TRUE":
                dct["required"] = True
            else:
                dct["required"] = False

        # Description
        if settings["description"]:
            dct["help"] = BRIGHT_YELLOW + settings["description"] + ENDC
        else:
            dct["help"] = None

        # An action of "append" requires a type of str and no default at all
        if settings["action"] == "append":
            dct["type"] = str
            if "default" in dct.keys():
                del dct["default"]

        # Positional arguments require that there be no dest or required
        if (not settings["short_flag"].startswith("-") and
            not settings["long_flag"].startswith("-")):
            if "dest" in dct.keys():
                del dct["dest"]
            if "required" in dct.keys():
                del dct["required"]

        # There is no such thing as a bool type, but users might type it in
        if settings["type"] is "bool":
            if "type" in dct.keys():
                del dct["type"]

        # If the actual type is a boolean as defined by the action, we cannot
        # have metavars or nargs
        if (settings["action"] is "store_true" or
            settings["action"] is "store_false"):
            if "metavar" in dct.keys():
                del dct["metavar"]
            if "nargs" in dct.keys():
                del dct["nargs"]

        # If nargs is not an integer, remove the metavar
        if "nargs" in dct.keys() and dct["nargs"] in ["?", "*", "+"]:
            if "metavar" in dct.keys():
                del dct["metavar"]

        return lst, dct

    # --------------------------------------------------------------------------
    @staticmethod
    def format_multi_line(items):
        """
        Given a list of items, re-formats it into a string, where each item
        is on its own line.

        :param items: A list of items.

        :return: A string where each list item is on its own line.
        """

        output = list()
        for item in items:
            output.append(item[0])
        return "\n".join(output)
