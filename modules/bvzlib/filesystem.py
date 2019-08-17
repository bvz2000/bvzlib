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


# ------------------------------------------------------------------------------
def seq_and_udim_ids_to_regex(path,
                              match_hash_length=False,
                              udim_identifier=None,
                              strict_udim_format=True):
    """
    Given a file string that may have a UDIM identifier and/or a sequence
    identifier in it, return the same string, but converted to a regex pattern
    that would match the UDIM and/or sequence patterns.

    For example, given an input like:

    /tmp/file_<UDIM>.####.exr

    Returns (assuming strict udim format and not matching the hash length):

    \/tmp\/file_[1-9]\d{3}\.\d+\.exr

    The UDIM identifier is defined by the calling function. If the UDIM
    identifier occurs more than once in the path, only the first occurrence will
    be used. A sequence identifier is either any number of hash symbols
    following a dot or underscore, or a string in the printf format (%0d). If
    both printf and the hash symbols are present, only the printf format will be
    recognized as a sequence identifier. If the printf sequence identifier or
    the hash symbols identifier occurs more than once in the path, only the
    first occurrence will be used.

    :param path: The path to the file name that may contain UDIM identifiers.
    :param match_hash_length: If True, then the output regex will be designed
           such that the number of digits has to match the number of hashes.
           If False, then a single hash would match any number of digits.
           For example: if True, then filename.#.exr would only match files with
           a single digit sequence number. If False, then any sequence number,
           no matter how long, would match. If the sequence identifier is in the
           printf format, this argument is ignored.
    :param udim_identifier: The string that is used as the UDIM identifier. If
           None, then the pattern "<UDIM>" will be used. Defaults to None.
    :param strict_udim_format: If True, then UDIM's will have to conform to the
           #### format, where the starting value is 1001. If False, then the
           UDIM must start with four digits, but can then contain any extra
           characters. Substance Painter allows this for example. Note, setting
           this to False may lead to somewhat erroneous identification of UDIM's
           in files, so - unless absolutely needed - this should be se to True.
           Defaults to True.

    :return: A string where the UDIM identifier, if it exists, is replaced with
             a regex pattern that matches this identifier.
    """

    parent_d, file_n = os.path.split(path)

    udim_split = udim_id_to_regex(file_n,
                                  udim_identifier,
                                  strict_udim_format)

    # Check both the first and last element of the udim_split for a sequence id
    prefix_seq_split = seq_id_to_regex(udim_split[0],
                                       match_hash_length)
    suffix_seq_split = seq_id_to_regex(udim_split[2],
                                       match_hash_length)

    # Assemble everything into a single string again
    output = re.escape(os.path.join(parent_d, prefix_seq_split[0]))
    output += prefix_seq_split[1]  # <- might have seq regex pattern in it.
    output += re.escape(prefix_seq_split[2])
    output += udim_split[1]  # <- might have UDIM regex pattern it in.
    output += re.escape(suffix_seq_split[0])
    output += suffix_seq_split[1]  # <- might have seq regex pattern in it.
    output += re.escape(suffix_seq_split[2])

    return output


# ------------------------------------------------------------------------------
def udim_id_to_regex(string,
                     udim_identifier=None,
                     strict_udim_format=True):
    """
    Given a string that may have a UDIM identifier in it, return the same
    string split into three elements: The prefix, the udim identifier converted
    to a regular expression, and the suffix.

    For example, given an input like:

    file_<UDIM>.exr

    Returns (assuming strict udim format):

    ("file_[1-9]", "\d{3}", ".exr")

    The UDIM identifier is defined by the calling function. If the UDIM
    identifier occurs more than once in the path, only the first occurrence will
    be used.

    :param string: The string that may contain UDIM identifiers.
    :param udim_identifier: The string that is used as the UDIM identifier. If
           None, then the pattern "<UDIM>" will be used. Defaults to None.
    :param strict_udim_format: If True, then UDIM's will have to conform to the
           #### format, where the starting value is 1001. If False, then the
           UDIM must start with four digits, but can then contain any extra
           characters. Substance Painter allows this for example. Note, setting
           this to False may lead to somewhat erroneous identification of UDIM's
           in files, so - unless absolutely needed - this should be se to True.
           Defaults to True.

    :return: A tuple containing three items: The portion of the text before the
             UDIM identifier, the UDIM identifier converted to a regular
             expression, and the portion of the text after the identifier. Note:
             The portions before and after the identifier may have special
             characters in them that will need to be escaped before thy could be
             used in a regular expression. If the UDIM identifier is not found,
             returns the original string in the first element of the tuple, and
             blank strings in the other two elements.
    """

    if udim_identifier is None:
        udim_identifier = "<UDIM>"

    input_pattern = r'.*?(' + re.escape(udim_identifier) + ').*'

    result = re.match(input_pattern, string)

    if result:
        identifier = result.groups()[0]

        prefix, suffix = string.split(identifier, 1)

        if strict_udim_format:
            output_pattern = "[1-9]\d{3}"
        else:
            output_pattern = "[1-9]\d{3}.*"

        return prefix, output_pattern, suffix

    return string, "", ""


# ------------------------------------------------------------------------------
def seq_id_to_regex(string,
                    match_hash_length=False):
    """
    Given a file string that may have a sequence identifier in it, return the
    same string, but converted to a regex pattern that would match the same
    sequence pattern.

    For example, given an input like:

    /tmp/file.#.exr

    Returns:

    \/tmp\/file\.\d+\.exr

    A sequence identifier is either any number of hash symbols following a dot
    or underscore, or a string in the printf format (%0d). If both printf and
    the hash symbols are present, only the printf format will be recognized as a
    sequence identifier. If the printf sequence identifier or the hash symbols
    identifier occurs more than once in the path, only the first occurrence will
    be used.

    :param string: The string that may contain sequence identifiers.
    :param match_hash_length: If True, then the output regex will be designed
           such that the number of digits has to match the number of hashes.
           If False, then a single hash would match any number of digits.
           For example: if True, then filename.#.exr would only match files with
           a single digit sequence number. If False, then any sequence number,
           no matter how long, would match. If the sequence identifier is in the
           printf format, this argument is ignored.

    :return: A tuple containing three items: The portion of the text before the
             seq identifier, the seq identifier converted to a regular
             expression, and the portion of the text after the identifier. Note:
             The portions before and after the identifier may have special
             characters in them that will need to be escaped before thy could be
             used in a regular expression. If the seq identifier is not found,
             returns the original string in the first element of the tuple, and
             blank strings in the other two elements.
    """

    test_pattern = r'[\._]%\d+d'
    printf_input_pattern = r'.*?()(%\d+d).*'  # Blank group is intentional
    hash_input_pattern = r'.*?([\._])(#+).*'

    do_printf = re.search(test_pattern, string)
    if do_printf:
        result = re.match(printf_input_pattern, string)
    else:
        result = re.match(hash_input_pattern, string)

    if result:
        delim, identifier = result.groups()

        if do_printf:
            length = str(int(identifier[1:-1]))
        else:
            if match_hash_length:
                length = str(len(identifier))
            else:
                length = None

        prefix, suffix = string.split(delim + identifier, 1)

        if length:
            output_pattern = re.escape(delim) + "\d{" + length + "}"
        else:
            output_pattern = re.escape(delim) + "\d+"

        return prefix, output_pattern, suffix

    return string, "", ""


# ------------------------------------------------------------------------------
def expand_frame_spec(file_n,
                      padding=None):
    """
    Given a string of the format (for example):

    this_is_a_sequence.1001-2300.exe

    Returns an expanded list of files. i.e. a list of:

    this_is_a_sequence.1001.exe
    this_is_a_sequence.1002.exe
    this_is_a_sequence.1003.exe
    etc..

    It can accept formats similar to:

    1001
    1001-2300
    1001-2300x2
    1001-2300:2
    1001-2300x2,2400-2500
    1001-2300x2@,2400-2500@
    etc.

    these numbers must be separated from the rest of the file name by a period
    or comma. There must be a dash between values if it is more than a single
    frame.
    Does not verify that the files actually
    exist.

    :param file_n: The string representing the file sequence.
    :param padding: The number of digits to pad the frame numbers to. A padding
           of 1 would mean no padding. If set to None, then the padding will be
           automatically determined based on the length of the longest frame
           number. Defaults to None.

    :return: A list of files.
    """

    # TODO: I think the @ symbol is on the wrong side of the frame step

    output = list()

    pattern = r"(?:\.|,)(\d+(?:(?:-\d+)?))@?(?:(?:[x:]([1-9]+))*)"

    path, name = os.path.split(file_n)

    compiled_pattern = re.compile(pattern)

    padding_len = 0
    match_start = len(name)
    match_end = 0
    for match in compiled_pattern.finditer(name):
        frame_range, step = match.groups()
        match_start = min(match_start, match.start())
        match_end = max(match_end, match.end())
        padding_len = max(padding_len, len(frame_range.split("-")[0]))
        try:
            padding_len = max(padding_len, len(frame_range.split("-")[1]))
        except IndexError:
            pass

    if padding:
        padding_len = padding

    for match in compiled_pattern.finditer(name):
        frame_range, step = match.groups()

        start = int(frame_range.split("-")[0])
        try:
            end = int(frame_range.split("-")[1])
        except IndexError:
            end = start

        try:
            step = int(step)
        except (TypeError, ValueError):
            step = 1

        for i in range(start, end + 1, step):
            output_str = name[:match_start + 1]
            output_str += str(i).rjust(padding_len, "0")
            output_str += name[match_end:]
            output_str = os.path.join(path, output_str)

            output.append(output_str)

    if not output:
        output = [file_n]

    return output


# ------------------------------------------------------------------------------
def expand_files(user_pattern,
                 padding=None,
                 udim_identifier=None,
                 strict_udim_format=True,
                 match_hash_length=False,
                 ):
    """
    Given a single pattern that may include frame specs, UDIM identifiers,
    and/or sequence identifiers, returns a list of actual files on disk that
    match these patterns.

    For example, the pattern:

    /tmp/file_name_%03d_<UDIM>.1-3.exr

    might expand out to:

    /tmp/file_name_001_1001.1.exr
    /tmp/file_name_001_1001.2.exr
    /tmp/file_name_001_1001.3.exr
    /tmp/file_name_001_1002.1.exr
    /tmp/file_name_001_1002.2.exr
    /tmp/file_name_001_1002.3.exr
    etc.

    assuming these files actually exist on disk.

    :param user_pattern: The pattern that describes the files on disk, usually
           provided by an end user.

           Formats allowed are:

           sequence specs (example: 1-10:2,12),
           UDIM patterns (example: <UDIM>),
           sequence identifiers (example: .### or %03d)

           See above for an example of an actual pattern.
    :param padding: Any padding to use when expanding frame specs. If None, then
           the padding will be determined from the longest number in the
           sequence. Defaults to None.
    :param udim_identifier: The string that is used as the UDIM identifier. If
           None, then the pattern "<UDIM>" will be used. Defaults to None.
    :param strict_udim_format: If True, then UDIM's will have to conform to the
           #### format, where the starting value is 1001. If False, then the
           UDIM must start with four digits, but can then contain any extra
           characters. Substance Painter allows this for example. Note, setting
           this to False may lead to somewhat erroneous identification of UDIM's
           in files, so - unless absolutely needed - this should be se to True.
           Defaults to True.
    :param match_hash_length: If True, then the output regex will be designed
           such that the number of digits has to match the number of hashes.
           If False, then a single hash would match any number of digits.
           For example: if True, then filename.#.exr would only match files with
           a single digit sequence number. If False, then any sequence number,
           no matter how long, would match. If the sequence identifier is in the
           printf format, this argument is ignored.

    :return: A list of absolute paths to the files represented by the pattern.
    """

    output = list()

    parent_d, file_pattern_n = os.path.split(os.path.abspath(user_pattern))

    assert os.path.exists(parent_d)
    assert os.path.isdir(parent_d)

    files_n = os.listdir(parent_d)

    expanded_user_patterns = expand_frame_spec(file_pattern_n, padding)
    for expanded_user_pattern in expanded_user_patterns:

        re_pattern = seq_and_udim_ids_to_regex(expanded_user_pattern,
                                               match_hash_length,
                                               udim_identifier,
                                               strict_udim_format)

        for file_n in files_n:
            if re.match(re_pattern, file_n):
                output.append(os.path.join(parent_d, file_n))

    return output


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


# ------------------------------------------------------------------------------
def symlinks_to_real_paths(symlinks_p):
    """
    Given a list of symbolic link files, return a list of their real paths. Only
    works on Unix-like systems for the moment.

    :param symlinks_p: The list of symlinks. If a file in this list is not
           a symlink, its path will be included unchanged.

    :return: A list of the real paths being pointed to by the symlinks. No
             assurances are given about the order of the returned paths
             as compared to the order of the given symlinks.
    """

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

    if type(source_dirs_d) != list:
        source_dirs_d = [source_dirs_d]

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

    md5 = hashlib.md5()
    with open(file_p, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.digest()


# ------------------------------------------------------------------------------
def compare_files(file_a_p,
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

    shutil.copy(src,
                dst)

    src_md5 = md5_for_file(src)
    dst_md5 = md5_for_file(dst)

    if not src_md5 == dst_md5:
        msg = "Verification of copy failed (md5 checksums to not match): "
        raise IOError(msg + src + " --> " + dst)


# --------------------------------------------------------------------------
def files_keyed_by_size(path_d):
    """
    Builds a dictionary of file sizes in a directory. The key is the file size,
    the value is a list of file names.

    :param path_d: The dir that contains the files we are evaluating. Does not
           traverse into sub-directories.

    :return: A dict where the key is the file size, the value is a list of paths
             to the files of this size.
    """

    output = dict()

    if not os.path.exists(path_d):
        return output

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

    source_d, source_n = os.path.split(source_p)
    base, ext = os.path.splitext(source_n)

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


# --------------------------------------------------------------------------
def copy_file_deduplicated(source_p,
                           dest_p,
                           data_d,
                           data_sizes,
                           ver_prefix="v",
                           num_digits=4):
    """
    Given a full path to a source file, copy that file into the data directory
    and make a symlink in dest_p that points to this file. Does de-duplication
    so that if more than one file (regardless of when copied or name) contains
    the same data, it will only be stored in data_d once.

    :param source_p: The path to the source file being stored.
    :param dest_p: The full path where the file will appear to be stored. In
           fact this will become a symlink to actual file in data_d.
    :param data_d: The directory where the actual files will be
           stored.
    :param data_sizes: A dictionary of all the files in the data_d keyed on file
           size. The key is the file size, the value is a list of files in
           data_d that are of that size.
    :param ver_prefix: The prefix to put onto the version number. For example,
           if the prefix is "v", then the version number will be represented as
           "v####". Defaults to "v".
    :param num_digits: How much padding to use for the version numbers. For
           example, 4 would lead to versions like: v0001 whereas 3 would lead to
           versions like: v001. Defaults to 4.

    :return: The path to the actual de-duplicated file in data_d.
    """

    # Make sure that the dest_p is not a sub-dir of data_d. Do some other tests.
    assert not dest_p.startswith(data_d)
    assert os.path.exists(source_p)
    assert os.path.exists(data_d)
    assert os.path.isdir(data_d)
    assert not os.path.isdir(source_p)
    assert type(data_sizes) == dict

    # Get the size of the current file
    size = os.path.getsize(source_p)

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
        matched_p = copy_and_add_ver_num(source_p, data_d, ver_prefix,
                                         num_digits)

    # Lock this file to the extent that we can
    os.chmod(matched_p, 0o644)

    # Build a relative path from where the symlink will go to the file in
    # the data dir. Then create a symlink to this file in the destination.
    dest_parent_p = os.path.split(dest_p.rstrip(os.path.sep))[0]
    matched_file_n = os.path.split(matched_p.rstrip(os.path.sep))[1]
    relative_d = os.path.relpath(data_d, dest_parent_p)
    relative_p = os.path.join(relative_d, matched_file_n)
    if os.path.exists(dest_p):
        os.unlink(dest_p)
    os.symlink(relative_p, dest_p)

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

        # Check to see if we are at the root level (bail if we are)
        if os.path.dirname(test_p) == test_p:
            if already_at_root:
                return None
            already_at_root = True
