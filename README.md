# bvzlib

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

Description
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

general
--------------------------------------------------------------------------------
Just a collection of generic functions that I reuse all of the time.



installation:
================================================================================

The bvzlib modules were written in python 2.7.

The bvzlib modules were written on a Linux system running Manjaro. They are 
compatible with any Linux system with the appropriate version of Python 
installed. They are also compatible with MacOS systems, assuming they too have 
Python 2.7 installed. These modules *should* also be compatible with Windows,
though I have yet to test this theory.

Installation is fairly straightforward.

1) Install bvzlib anywhere you like, and make sure that it is also added to
your PYTHONPATH. For example, if you install the bvz package to:

/opt/apps/studio/bvzlib

then you will want to add the following path to your PYTHONPATH:

/opt/apps/studio/bvzlib/modules

After that the libraries will be available to any tools that require them.