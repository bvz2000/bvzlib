import os
import re


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
def find_frame_spec(string):
    """
    Finds the framespec in a string. Does NOT break it out into its constituent
    components (start, end, step).

    :param string: The string to search.

    :return: A tuple with three elements: The string leading up to the last
             framespec found, the framespec itself, and the string following the
             framespec. For example: ("filename", ".1-10x2,20,30,32-40.", "tif")
    """

    # Complete regex pattern is here, rebuilt in pieces below
    # (?:(?<=\.)|(?<=^))(?:(?:(?<!\.),)?\d+(?:-\d+(?:[x:]-?\d+)?)?)+(?:@+|#+)?(?=\.|$)

    # Always start with a dot or beginning of line (negative lookbehind).
    fspec_pattern = r"(?:(?<=\.)|(?<=^))"

    # Actual framespec (repeat as many times as needed)
    fspec_pattern += r"(?:(?:(?<!\.),)?\d+(?:-\d+(?:[x:]-?\d+)?)?)+"

    # May contain an optional string of # or @ symbols at the end.
    fspec_pattern += r"(?:@+|#+)?"

    # And is followed with a dot or the end of the line (positive lookahead)
    fspec_pattern += r"(?=\.|$)"

    compiled_pattern = re.compile(fspec_pattern)

    # Separate the last framespec in the file name (only the last one counts)
    match_start = None
    match_end = None

    for match in compiled_pattern.finditer(string):

        if match_start:
            match_start = max(match_start, match.start())
        else:
            match_start = match.start()

        if match_end:
            match_end = max(match_end, match.end())
        else:
            match_end = match.end()

    if match_start is None or match_end is None:
        return string, "", ""

    prefix = string[:match_start]
    suffix = string[match_end:]
    framespec = string[match_start:match_end]

    return prefix, framespec, suffix


# ------------------------------------------------------------------------------
def expand_frame_spec(framespec):
    """
    Given a framespec, return a list of frame numbers that match. For example:
    Given 1-5x2,8, return [1,3,5,8]

    Expects a valid framespec. If you give it something that contains non-valid
    framespec values, the result is undefined.

    :param framespec: The framespec string

    :return: A list of numbers this framespec evaluates to.
    """

    fspec_pattern = r"(\d+)(?:(?:-(\d+))(?:[x:](-?\d+))?)?"
    compiled_pattern = re.compile(fspec_pattern)

    output = set()

    for subspec in framespec.split(","):

        for matches in compiled_pattern.finditer(subspec):

            start, end, step = matches.groups()

            start = int(start)

            if not end:
                end = start
            else:
                end = int(end)

            if not step:
                step = 1
            else:
                step = int(step)

            if step > 0:
                offset = 1
            else:
                offset = -1

            for i in range(start, end + offset, step):
                output.add(i)

    output = sorted(output)

    return output


# ------------------------------------------------------------------------------
def calc_padding(frames, framespec=None, padding=None):
    """
    Given a list of frame numbers, a framespec, and a padding length, return a
    modified padding value. I.e. if padding is None, returns 1. If padding is 0
    then it will figure out the length of the longest frame and return that. If
    framespec is not None and the framespec has a padding set in it, returns
    that.

    If framespec is None, thenIf padding is None, returns a padding of 1 (i.e.
    no padding). Defaults to None.

    :param frames: A list of integers.
    :param framespec: A framespec string. Defaults to None.
    :param padding: How many digits to pad out to. Defaults to None.

    :return: An actual padding value
    """

    if padding is None:
        return 1

    if padding == 0:
        if frames:
            return len(str(max(frames)))
        else:
            return 1

    if framespec:

        if "#" in framespec:
            return len(framespec.split("#", 1)[1]) + 1

        if "@" in framespec:
            return len(framespec.split("@", 1)[1]) + 1

    return int(padding)


# ------------------------------------------------------------------------------
def expand_frame_sequence(file_n,
                          padding=None):
    """
    Given a string of the format (for example):

    filename.1-10.exe

    Returns an expanded list of files. i.e. a list of:

    filename.1.exe
    filename.2.exe
    filename.3.exe
    etc..

    It can accept formats similar to:

    1
    1-10
    1-10x2
    1-10:2
    1-10,20-30
    1-10x2,20-30x2
    1-10,20-30@
    1-10,20-30@@
    1-10,20-30#
    1-10,20-30##
    10-1x-1
    etc.

    these numbers must be separated from the rest of the file name by a period.
    There must be a dash between values if it is more than a single frame.
    Does not verify that the files actually exist.

    :param file_n: The string representing the file sequence.
    :param padding: The number of digits to pad the frame numbers to. If None,
           then no padding will be added. If 0, then the padding will be based
           on the longest frame number in the sequence. If set to anything other
           than None or 0, then the padding will be set to that value. Note:
           the padding may also be described by using the @@@ or ### indicator
           in the sequence spec itself. That said, using the padding argument in
           this method (if set to any value other than None) will override the
           padding given in the format of @@@ or ### in the frame spec string.
           Defaults to None.

    :return: A list of files. These files may or may not exist on disk.
    """

    output = list()

    path, name = os.path.split(file_n)

    prefix, framespec, suffix = find_frame_spec(name)

    frames = expand_frame_spec(framespec)

    if not frames:
        return [file_n]

    padding = calc_padding(frames, framespec, padding)

    for frame in frames:

        file_out_n = prefix + str(frame).rjust(padding, "0") + suffix
        output.append(os.path.join(path, file_out_n))

    return output


# ------------------------------------------------------------------------------
def expand_files(user_pattern,
                 padding=None,
                 udim_identifier=None,
                 strict_udim_format=True,
                 match_hash_length=False):
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
           no padding will be used. Defaults to None.
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
    missing = list()

    parent_d, file_pattern_n = os.path.split(os.path.abspath(user_pattern))

    assert os.path.exists(parent_d)
    assert os.path.isdir(parent_d)

    prefix, framespec, suffix = find_frame_spec(file_pattern_n)

    if not framespec or not suffix:
        frames = list()
    else:
        frames = expand_frame_spec(framespec)

    actual_padding = calc_padding(frames, framespec, padding)

    prefix_pattern = seq_and_udim_ids_to_regex(prefix,
                                               match_hash_length,
                                               udim_identifier,
                                               strict_udim_format)

    suffix_pattern = seq_and_udim_ids_to_regex(suffix,
                                               match_hash_length,
                                               udim_identifier,
                                               strict_udim_format)

    files_n = os.listdir(parent_d)

    if frames:

        for frame in frames:

            matched = False

            if not padding:
                frame_pattern = "0*" + str(frame)
            else:
                frame_pattern = str(frame).rjust(actual_padding, "0")

            pattern = prefix_pattern + frame_pattern + suffix_pattern

            for file_n in files_n:

                if re.match(pattern, file_n):
                    output.append(os.path.join(parent_d, file_n))
                    matched = True

            if not matched:
                missing.append(frame)

    else:

        output = [os.path.join(parent_d, file_pattern_n)]

    missing.sort()
    for i in range(len(missing)):
        missing[i] = str(missing[i]).rjust(actual_padding, "0")

    output.sort()
    return output, missing
