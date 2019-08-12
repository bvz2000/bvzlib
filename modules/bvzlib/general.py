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


# ------------------------------------------------------------------------------
def merge_lists_unique(list1, list2, case_sensitive=True):
    """
    Given two lists, merge them so that there are no duplicates. Always case
    preserving regardless of case_sensitivity. If case_sensitivity is False,
    the case for any overlapping items will be taken from list1. The order of
    the returned list is undefined.

    :param list1: The first list.
    :param list2: The second list.
    :param case_sensitive: Whether to consider case when matching. If True, then
           'abc' will be considered unique from 'ABC'. If False, then these two
           would be considered duplicates of each other. Defaults to True.

    :return: A merged list with no duplicate items.
    """

    dict1 = dict()
    dict2 = dict()
    output = list()

    for item in list1:
        if case_sensitive:
            dict1[item] = item
        else:
            dict1[item.lower()] = item

    for item in list2:
        if case_sensitive:
            dict2[item] = item
        else:
            dict2[item.lower()] = item

    for key in dict1.keys():
        dict2[key] = dict1[key]

    for key in dict2.keys():
        output.append(dict2[key])

    return output
