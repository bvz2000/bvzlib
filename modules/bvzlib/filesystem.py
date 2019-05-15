import hashlib
import os
import re
import shutil


# # ------------------------------------------------------------------------------
# def expand_udims(path):
#     """
#     Given a file with '<UDIM>' in the path name, expand that to a list of actual
#     files on disk.
#
#     :param path: The path with the text <UDIM> in it.
#
#     :return: A list of files that the path represents. Only actual files on disk
#              will be returned.
#     """
#
#     assert "<UDIM>" in path
#
#     output = list()
#
#     parent_d, file_n = os.path.split(path)
#     base_n, end_n = file_n.split("<UDIM>")
#
#     files = os.listdir(parent_d)
#     for test_n in files:
#         if test_n.startswith(base_n) and test_n.endswith(end_n):
#             output.append(os.path.join(parent_d, test_n))
#
#     return output
#
#
# # ------------------------------------------------------------------------------
# def expand_sequences(path):
#     """
#     Given a file with '.#' in the path name (with any number of # symbols),
#     expand that to a list of actual files on disk.
#
#     :param path: The path with the text .# (with any number of # symbols) in it.
#
#     :return: A list of files that the path represents. Only actual files on disk
#              will be returned.
#     """
#
#     assert ".#" in path
#
#     output = list()
#
#     parent_d, file_n = os.path.split(path)
#
#     pattern = '(.*)(\.#+)(.*)'
#     result = re.match(pattern, file_n)
#
#     base_n = result.groups()[0]
#     end_n = result.groups()[2]
#
#     files = os.listdir(parent_d)
#     for test_n in files:
#         if test_n.startswith(base_n) and file_n.endswith(end_n):
#             output.append(os.path.join(parent_d, test_n))
#
#     return output

# --------------------------------------------------------------------------
def invert_dir_list(parent_d, subdirs_n, pattern=None):
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
    Given a list of symbolic link files, return a list of their real paths.

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
def md5_for_file(file_p, block_size=2**20):
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
def verified_copy_file(src, dst):
    """
    Given a source file and a destination, copies the file, and then checksum's
    both files to ensure that the copy matches the source.

    :param src: The source file to be copied.
    :param dst: The destination file name where the file will be copied. If the
           destination file already exists, an error will be raised. You must
           supply the destination file name, not just the destination dir.

    :return: True if the copy was successful. False otherwise.
    """

    shutil.copy(src, dst)

    src_md5 = md5_for_file(src)
    dst_md5 = md5_for_file(dst)

    return src_md5 == dst_md5


# --------------------------------------------------------------------------
def get_file_sizes(path_d):
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
def copy_and_add_ver_num(source_p, dest_d, ver_prefix="v", num_digits=4):
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

        shutil.copy(source_p, dest_p)

        return dest_p


# --------------------------------------------------------------------------
def copy_file_deduplicated(source_p, dest_p, data_d, data_sizes, ver_prefix="v",
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

    :return: Nothing.
    """
    # TODO: Do a verified copy and report back the result
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
    os.symlink(relative_p, dest_p)
