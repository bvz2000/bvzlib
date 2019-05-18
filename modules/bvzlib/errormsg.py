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
