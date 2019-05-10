#! /usr/bin/env python2

import ConfigParser

import os

import errormsg


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


# ==============================================================================
class Resources(ConfigParser.SafeConfigParser):
    """
    Class to manage the resources file. Subclassed from the default python
    config parser.
    """

    # --------------------------------------------------------------------------
    def __init__(self, resources_d, prefix, language="english"):
        """
        Setup this subclass of the default python config parser.

        :param resources_d: The directory where the resources files are stored.
        :param prefix: The prefix for the resources file. For example, if you
               want to read the "squirrel_resources_english.ini" resources file,
               the prefix would be: "squirrel". Required.
        :param language: The language to use when parsing the resources file. If
               no language is supplied, defaults to "english".

        :return: Nothing.
        """

        ConfigParser.SafeConfigParser.__init__(self, allow_no_value=True)

        self.resources_d = resources_d
        self.resources_n = prefix + "_resources_" + language + ".ini"
        self.resources_p = os.path.join(self.resources_d, self.resources_n)
        self.read_resources()

    # --------------------------------------------------------------------------
    def read_resources(self):
        """
        Opens up the appropriate resource file and reads its contents.

        :return: Nothing.
        """

        # If this file does not exist, warn the user and bail. Since we cannot
        # find a language yet, report the error in English.
        if not os.path.exists(self.resources_p):
            msg = "Cannot locate resource file: " + self.resources_p
            raise IOError(msg)

        # Open and populate the resources object
        self.read(self.resources_p)

    # --------------------------------------------------------------------------
    @staticmethod
    def format_string(msg):
        """
        Given a string (msg) this will format it with colors based on the
        {{COLOR}} tags. (example {{COLOR_RED}}). It will also convert literal \n
        character string into a proper newline.

        :param msg: The string to format.

        :return: The formatted string.
        """

        output = msg.replace(r"\n", "\n")

        output = output.replace("{{COLOR_BLACK}}", BLACK)
        output = output.replace("{{COLOR_RED}}", RED)
        output = output.replace("{{COLOR_GREEN}}", GREEN)
        output = output.replace("{{COLOR_YELLOW}}", YELLOW)
        output = output.replace("{{COLOR_BLUE}}", BLUE)
        output = output.replace("{{COLOR_MAGENTA}}", MAGENTA)
        output = output.replace("{{COLOR_CYAN}}", CYAN)
        output = output.replace("{{COLOR_WHITE}}", WHITE)
        output = output.replace("{{COLOR_BRIGHT_RED}}", BRIGHT_RED)
        output = output.replace("{{COLOR_BRIGHT_GREEN}}", BRIGHT_GREEN)
        output = output.replace("{{COLOR_BRIGHT_YELLOW}}", BRIGHT_YELLOW)
        output = output.replace("{{COLOR_BRIGHT_BLUE}}", BRIGHT_BLUE)
        output = output.replace("{{COLOR_BRIGHT_MAGENTA}}", BRIGHT_MAGENTA)
        output = output.replace("{{COLOR_BRIGHT_CYAN}}", BRIGHT_CYAN)
        output = output.replace("{{COLOR_BRIGHT_WHITE}}", BRIGHT_WHITE)
        output = output.replace("{{COLOR_NONE}}", ENDC)

        return output

    # --------------------------------------------------------------------------
    def error(self, code):
        """
        Extracts the error message associated with the code.

        :param code: The code for the error message.

        :return: An error object.
        """

        err = errormsg.ErrorMsg()

        msg = self.get("error_codes", str(code))
        msg = self.format_string(msg)

        err.msg = msg
        err.code = int(code)

        return err

    # --------------------------------------------------------------------------
    def message(self, message_key):
        """
        Extracts the message associated with the key.

        :param message_key: The key for the message.

        :return: A string.
        """

        msg = self.get("messages", str(message_key))
        msg = self.format_string(msg)

        return msg
