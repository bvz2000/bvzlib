# bvzlib

--------------------------------------------------------------------------------
A series of python libraries that I use in most of my projects.

These libraries (at the time of writing) are:

config:
--------------------------------------------------------------------------------
A library to read .ini files used for end user configuration of an app. This is
just a thin wrapper around ConfigParser that knows how to automatically read in
a .ini file. This file is either passed directly as an absolute path, or it is
given as an env variable so that the end user can redirect where the app reads
its configuration from.

filesystem:
--------------------------------------------------------------------------------
A series of generic functions that interact with the filesystem.

options
--------------------------------------------------------------------------------
An object that wraps argparse. It allows a command line tool's arguments to be
defined in a simple text file (another .ini file managed by resources described
below). No additional coding is then needed to set up command line args if using
this module.

resources
--------------------------------------------------------------------------------
Yet another wrapper around ConfigParser (I guess I really love .ini files).
This is designed to load and read a resources file. This resources file contains
all of the strings for an app in a particular language. It also contains the
args for the options module above (if needed). An example of this resources
file can be seen in the resources directory of this package.