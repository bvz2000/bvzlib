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

import hashlib
import os
import re
import shutil


# --------------------------------------------------------------------------
def invert_dir_list(parent_d,
                    subdirs_n,
                    pattern=None):
    """
    Given a parent directory and a list of directory names, returns any other
    directories in this parent dir that are not in this list (effectively
    inverting the list of sub directories).

    :param parent_d: The directory containing the sub-dirs we are trying to
           invert.
    :param subdirs_n: A list of sub-directories that are the inverse of the ones
           we want to return.
    :param pattern: An optional regex pattern to limit our inverse to. If None,
           then all sub directories will be included. Defaults to None.

    :return: A list of all sub directories in parent_d that are not in the list
             subdirs_n.
    """

    assert os.path.exists(parent_d)
    assert os.path.isdir(parent_d)
    assert type(subdirs_n) is list
    assert pattern is None or type(pattern) is str

    items_n = os.listdir(parent_d)
    output = list()

    for item_n in items_n:
        if os.path.isdir(os.path.join(parent_d, item_n)):
            if item_n not in subdirs_n:
                result = True
                if pattern:
                    result = re.match(pattern, item_n)
                if result:
                    output.append(item_n)

    return output


# ------------------------------------------------------------------------------
def convert_unix_path_to_os_path(path):
    """
    Given a path string (in a unix-like path format), converts it into an
    OS appropriate path format. Note, it does not check to see whether this
    path exists. It merely re-formats the string into the OS specific format.

    :param path: The path string to be reformatted.

    :return: An OS appropriate path string.
    """

    assert type(path) is str

    return os.path.join(*path.lstrip("/").split("/"))


# TODO: Make windows friendly
# ------------------------------------------------------------------------------
def symlinks_to_real_paths(symlinks_p):
    """
    Given a list of symbolic link files, return a list of their real paths. Only
    works on Unix-like systems for the moment.

    :param symlinks_p: The list of symlinks. If a file in this list is not
           a symlink, its path will be included unchanged. If a file in this
           list does not exist, it will be treated as though it is not a
           symlink.

    :return: A list of the real paths being pointed to by the symlinks.
    """

    assert type(symlinks_p) is list

    output = list()

    for symlink_p in symlinks_p:
        output.append(os.path.realpath(symlink_p))
    return output


# ------------------------------------------------------------------------------
def recursively_list_files_in_dirs(source_dirs_d):
    """
    Recursively list all files in a directory or directories

    :param source_dirs_d: a list of directories we want to recursively list.

    :return: A list of files with full paths that are in any of the directories
             (or any of their sub-directories)
    """

    assert type(source_dirs_d) is list
    for source_dir_d in source_dirs_d:
        assert os.path.exists(source_dir_d)

    output = list()

    for source_dir_d in source_dirs_d:
        for dir_d, sub_dirs_n, files_n in os.walk(source_dir_d):
            for file_n in files_n:
                output.append(os.path.join(dir_d, dir_d, file_n))
    return output


# ------------------------------------------------------------------------------
def md5_for_file(file_p,
                 block_size=2**20):
    """
    Create an md5 checksum for a file without reading the whole file in in a
    single chunk.

    :param file_p: The path to the file we are checksumming.
    :param block_size: How much to read in in a single chunk. Defaults to 1MB

    :return: The md5 checksum.
    """

    assert os.path.exists(file_p)
    assert type(block_size) is int

    md5 = hashlib.md5()
    with open(file_p, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.digest()


# ------------------------------------------------------------------------------
def files_are_identical(file_a_p,
                        file_b_p,
                        block_size=2**20):
    """
    Compares two files to see if they are identical. First compares sizes. If
    the sizes match, then it does an md5 checksum on the files to see if they
    match. Ignores all metadata when comparing (name, creation or modification
    dates, etc.) Returns True if they match, False otherwise.

    :param file_a_p: The path to the first file we are comparing.
    :param file_b_p: The path to the second file we are comparing
    :param block_size: How much to read in in a single chunk when doing the md5
           checksum. Defaults to 1MB

    :return: True if the files match, False otherwise.
    """

    assert os.path.exists(file_a_p)
    assert os.path.isfile(file_a_p)
    assert os.path.exists(file_b_p)
    assert os.path.isfile(file_b_p)

    if os.path.getsize(file_a_p) == os.path.getsize(file_b_p):
        md5_a = md5_for_file(file_a_p, block_size)
        md5_b = md5_for_file(file_b_p, block_size)
        return md5_a == md5_b

    return False


# ------------------------------------------------------------------------------
def verified_copy_file(src,
                       dst):
    """
    Given a source file and a destination, copies the file, and then checksum's
    both files to ensure that the copy matches the source. Raises an error if
    the copied file's md5 checksum does not match the source file's md5
    checksum.

    :param src: The source file to be copied.
    :param dst: The destination file name where the file will be copied. If the
           destination file already exists, an error will be raised. You must
           supply the destination file name, not just the destination dir.

    :return: Nothing.
    """

    assert os.path.exists(src)
    assert os.path.isfile(src)
    assert os.path.exists(os.path.split(dst)[0])
    assert os.path.isdir(os.path.split(dst)[0])

    shutil.copy(src, dst)

    if not files_are_identical(src, dst):
        msg = "Verification of copy failed (md5 checksums to not match): "
        raise IOError(msg + src + " --> " + dst)


# --------------------------------------------------------------------------
def dir_files_keyed_by_size(path_d):
    """
    Builds a dictionary of file sizes in a directory. The key is the file size,
    the value is a list of file names.

    :param path_d: The dir that contains the files we are evaluating. Does not
           traverse into sub-directories.

    :return: A dict where the key is the file size, the value is a list of paths
             to the files of this size.
    """

    assert os.path.exists(path_d)

    output = dict()

    files_n = os.listdir(path_d)
    for file_n in files_n:
        file_p = os.path.join(path_d, file_n)
        file_size = os.path.getsize(file_p)
        if file_size not in output.keys():
            output[file_size] = [file_p]
        else:
            existing_files = output[file_size]
            existing_files.append(file_p)
            output[file_size] = existing_files
    return output


# ------------------------------------------------------------------------------
def copy_and_add_ver_num(source_p,
                         dest_d,
                         dest_n=None,
                         ver_prefix="v",
                         num_digits=4,
                         do_verified_copy=False):
    """
    Copies a source file to the dest dir, adding a version number to the file
    right before the extension. If a file with that version number already
    exists, the file being copied will have its version number incremented so as
    not to overwrite.  Returns a full path to the file that was copied.

    :param source_p: The full path to the file to copy.
    :param dest_d: The directory to copy to.
    :param dest_n: An optional name to rename the copied file to. If None, then
           the copied file will have the same name as the source file. Defaults
           to None.
    :param ver_prefix: The prefix to put onto the version number. For example,
           if the prefix is "v", then the version number will be represented as
           "v####". Defaults to "v".
    :param num_digits: How much padding to use for the version numbers. For
           example, 4 would lead to versions like: v0001 whereas 3 would lead to
           versions like: v001. Defaults to 4.
    :param do_verified_copy: If True, then a verified copy will be performed.
           Defaults to False.

    :return: A full path to the file that was copied.
    """

    assert os.path.exists(source_p)
    assert os.path.isfile(source_p)
    assert os.path.exists(dest_d)
    assert os.path.isdir(dest_d)
    assert type(num_digits) is int
    assert type(do_verified_copy) is bool

    if not dest_n:
        source_d, dest_n = os.path.split(source_p)

    base, ext = os.path.splitext(dest_n)

    v = 1
    while True:

        version = "." + ver_prefix + str(v).rjust(num_digits, "0")
        dest_p = os.path.join(dest_d, base + version + ext)

        # This is not race condition safe, but it works for most cases...
        if os.path.exists(dest_p):
            v += 1
            continue

        if do_verified_copy:
            verified_copy_file(source_p, dest_p)
        else:
            shutil.copy(source_p, dest_p)

        return dest_p


# TODO: Make this windows safe
# ------------------------------------------------------------------------------
def copy_file_deduplicated(source_p,
                           dest_d,
                           data_d,
                           data_sizes,
                           dest_n=None,
                           ver_prefix="v",
                           num_digits=4,
                           do_verified_copy=False):
    """
    Given a full path to a source file, copy that file into the data directory
    and make a symlink in dest_p that points to this file. Does de-duplication
    so that if more than one file (regardless of when copied or name) contains
    the same data, it will only be stored in data_d once.

    :param source_p: The path to the source file being stored.
    :param dest_d: The full path of the directory where the file will appear to
           be stored. In actual fact this will really become a symlink to the
           actual file which will be stored in data_d. dest_d may not be a
           sub-directory of data_d.
    :param data_d: The directory where the actual files will be
           stored.
    :param data_sizes: A dictionary of all the files in the data_d keyed on file
           size. The key is the file size, the value is a list of files in
           data_d that are of that size.
    :param dest_n: An optional name to rename the copied file to. If None, then
           the copied file will have the same name as the source file. Defaults
           to None.
    :param ver_prefix: The prefix to put onto the version number. For example,
           if the prefix is "v", then the version number will be represented as
           "v####". Defaults to "v".
    :param num_digits: How much padding to use for the version numbers. For
           example, 4 would lead to versions like: v0001 whereas 3 would lead to
           versions like: v001. Defaults to 4.
    :param do_verified_copy: If True, then a verified copy will be performed.
           Defaults to False.

    :return: The path to the actual de-duplicated file in data_d.
    """

    assert not dest_d.startswith(data_d)
    assert os.path.exists(source_p)
    assert os.path.isfile(source_p)
    assert os.path.exists(data_d)
    assert os.path.isdir(data_d)
    assert os.path.exists(dest_d)
    assert os.path.isdir(dest_d)
    assert type(data_sizes) == dict
    for key in data_sizes:
        assert type(data_sizes[key]) == list
    assert type(num_digits) is int
    assert type(do_verified_copy) is bool

    size = os.path.getsize(source_p)

    if not dest_n:
        dest_n = os.path.split(source_p)[1]

    # Check to see if there is a list of files of that size in the .data dir
    try:
        possible_matches_p = data_sizes[size]
    except KeyError:
        possible_matches_p = []

    # For each of these, try to find a matching file
    matched_p = None
    source_md5 = md5_for_file(source_p)
    for possible_match_p in possible_matches_p:
        possible_match_md5 = md5_for_file(possible_match_p)
        if source_md5 == possible_match_md5:
            matched_p = possible_match_p
            break

    # If we did not find a matching file, then copy the file to the
    # data_d dir, with an added version number that ensures that we do
    # not  overwrite any previous versions of files with the same name.
    if matched_p is None:
        matched_p = copy_and_add_ver_num(source_p=source_p,
                                         dest_d=data_d,
                                         dest_n=dest_n,
                                         ver_prefix=ver_prefix,
                                         num_digits=num_digits,
                                         do_verified_copy=do_verified_copy)

    os.chmod(matched_p, 0o644)

    # Build a relative path from where the symlink will go to the file in
    # the data dir. Then create a symlink to this file in the destination.
    dest_d = dest_d.rstrip(os.path.sep)
    matched_file_n = os.path.split(matched_p.rstrip(os.path.sep))[1]
    relative_d = os.path.relpath(data_d, dest_d)
    relative_p = os.path.join(relative_d, matched_file_n)
    if os.path.exists(os.path.join(dest_d, dest_n)):
        os.unlink(os.path.join(dest_d, dest_n))
    os.symlink(relative_p, os.path.join(dest_d, dest_n))

    return matched_p


# ------------------------------------------------------------------------------
def ancestor_contains_file(path_p,
                           files_n,
                           depth=None):
    """
    Returns the path of any parent directory (evaluated recursively up the
    hierarchy) that contains any of the files in the list: files_n. This is
    typically used to see if any parent directory contains a semaphore file.
    For example: If your current path (where "current" just means some path
    you already have) is /this/is/my/path, and you want to see if any of the
    parent paths contain a specific file or files, then this method will allow
    you to do that.

    :param path_p: The path we are testing.
    :param files_n: A list of file names we are looking for.
    :param depth: Limit the number of levels up to look. If None, then the
           search will continue all the way up to the root level. Defaults to
           None. For example: a depth of 1 will only check the immediate parent
           of the given path. 2 will check the immediate parent and its parent.
           Searches will never progress "past" the root, regardless of depth.

    :return: The path of the first parent that contains any one of these files.
             If no ancestors contain any of these files, returns None.
    """

    assert depth is None or type(depth) is int
    assert os.path.exists(path_p)
    assert os.path.isdir(path_p)
    assert type(files_n) is str or type(files_n) is list

    if type(files_n) != list:
        files_n = [files_n]

    path_p = path_p.rstrip(os.path.sep)

    if not os.path.isdir(path_p):
        path_p = os.path.dirname(path_p)

    already_at_root = False
    count = 0

    test_p = os.path.dirname(path_p)
    while True:

        # Check each of the test files.
        for file_n in files_n:
            if os.path.exists(os.path.join(test_p, file_n)):
                return test_p

        # If nothing is found, move up to the next parent dir.
        test_p = os.path.dirname(test_p)

        # Increment the count and bail if we have hit our max depth.
        count += 1
        if depth and count >= depth:
            return None

        # TODO: Probably not windows safe
        # Check to see if we are at the root level (bail if we are)
        if os.path.dirname(test_p) == test_p:
            if already_at_root:
                return None
            already_at_root = True


# ------------------------------------------------------------------------------
def lock_dir(path_d):
    """
    Changes the permissions on a directory so that it is readable and
    executable, but may not be otherwise altered.

    :param path_p: The path to the directory we want to lock.

    :return: Nothing.
    """

    assert os.path.exists(path_d)
    assert os.path.isdir(path_d)

