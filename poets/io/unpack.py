# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Vienna University of Technology - Department of
#   Geodesy and Geoinformation nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-10-01

'''
Module for unpacking compressed archives. Based on pyunpack and patool.
'''

import os
import shutil
from pyunpack import Archive


def check_compressed(filepath):
    """
    Checks if a file is compressed using the file extension.

    Parameters
    ----------
    filepath : string
        Path to input file.

    Returns
    -------
    boolean
        True if compressed, False if not.
    """

    comp_ext = ['.zip', '.bz2', '.tar', '.7z', '.ace', '.rar', '.adf', '.alz',
                '.cab', '.Z', '.cpio', '.deb', '.dms', '.gz', '.iso', '.lrz',
                '.lha', '.lzh', '.lz', '.lzma', '.lzo', '.rpm', '.rz', '.shn',
                '.xz', '.zoo']

    if os.path.splitext(filepath)[1].lower() in comp_ext:
        return True
    else:
        return False


def flatten(outpath):
    '''
    Flattens directory structure.

    Parameters
    ----------
    outpath : str
        Directory to flatten.

    Raises
    ------
    OSError :
        If file cannot be moved.
    '''

    # move files
    for dirpath, dirnames, filenames in os.walk(outpath):
        for filename in filenames:
            try:
                os.rename(os.path.join(dirpath, filename),
                          os.path.join(outpath, filename))
            except OSError:
                print ("Could not move %s " % os.path.join(dirpath,
                                                           filename))
    # delete empty folders
    for dirpath, dirnames, filenames in os.walk(outpath):
        for directory in dirnames:
            shutil.rmtree(os.path.join(dirpath, directory))


def unpack(filepath, outpath=None):
    """
    Unpacks compressed archives and files recursively and flattens the output.

    Parameters
    ----------
    filepath : str
        Path to zipped archive.
    outpath : str
        Path where decompressed files will be stored.
    flatten : bool, optional
        If True, output dir will be flattened.

    Raises
    ------
    IOError :
        If input file does not exist.
    """

    if os.path.isfile(filepath):

        if outpath is None:
            outpath = os.path.splitext(filepath)[0]
            outpath = outpath.split(".")[0]

        if not os.path.exists(outpath):
            os.makedirs(outpath)

        Archive(filepath).extractall(outpath)

        flatten(outpath)

        for f in os.listdir(outpath):
            if check_compressed(f):
                unpack(os.path.join(outpath, f))
                os.unlink(os.path.join(outpath, f))

        flatten(outpath)

    else:
        raise IOError('%s file does not exist' % filepath)

