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
# Creation date: 2014-10-02

import os

supported_formats = ['.nc', '.nc4',
                     '.h5',
                     '.tiff', '.tif',
                     '.png', '.jpg', '.jpeg', '.gif']


def check_supported(filename):
    """Checks if file is in supported format.

    Parameters
    ----------
    filename : str
        Filename or filepath.

    Returns
    -------
    bool
        True if supported, False if not.
    """

    return os.path.splitext(filename)[1].lower() in supported_formats


def select_file(filelist):
    """Selects a file out of a list of files, based on their extension.

    Parameters
    ----------
    filelist : list of str
        List containing filepaths.

    Returns
    -------
    filename : str
        Filepath of selected file.

    Raises
    ------
    IOError :
        If filelist contains no supported file format.
    """

    extlist = []

    for f in filelist:
        fext = os.path.splitext(f)[1].lower()
        if fext in supported_formats:
            extlist.append(supported_formats.index(fext))
        else:
            extlist.append('X')

    val, idx = min((val, idx) for (idx, val) in enumerate(extlist))

    if val == 'X':
        raise IOError("No valid file format found.")
    else:
        return filelist[idx]

