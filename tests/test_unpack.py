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

# Author: Isabella Pfeil, isy.pfeil@gmx.at
# Creation date: 2014-11-24

import unittest
import os
import poets.io.unpack as up
import zipfile
import shutil


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))

    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.fname = os.path.join(curpath(), 'data', 'test.zip')
        self.outpath = os.path.join(curpath(), 'data', 'test')
        self.dirpath = os.path.join(curpath(), 'data', 'testdir')

    def tearDown(self):

        if os.path.exists(self.dirpath):
            shutil.rmtree(self.dirpath)
        if os.path.exists(os.path.join(curpath(), 'data', 'test2.txt')):
            os.remove(os.path.join(curpath(), 'data', 'test2.txt'))

    def test_check_compressed(self):
        test = up.check_compressed(self.fname)
        self.failUnless(test is True)

    def test_unpack(self):
        # create txt-file
        txt1 = open(os.path.join(curpath(), 'data', 'test1.txt'), 'w')
        txt1.close()

        # create first zip archive
        ziparc = zipfile.ZipFile(os.path.join(curpath(), 'data',
                                              'ziparc.zip'), 'w')

        # write txt-file and folder to zip archive
        ziparc.write(os.path.join(curpath(), 'data', 'test1.txt'))
        ziparc.close()

        # 'create' second txt-file
        os.rename(os.path.join(curpath(), 'data', 'test1.txt'),
                  os.path.join(curpath(), 'data', 'test2.txt'))

        # create second zip archive
        ziparc2 = zipfile.ZipFile(os.path.join(curpath(), 'data',
                                               'ziparc2.zip'), 'w')

        # write second txt-file and first zip archive to second zip archive
        ziparc2.write(os.path.join(curpath(), 'data', 'test2.txt'))
        ziparc2.write(os.path.join(curpath(), 'data', 'ziparc.zip'))
        ziparc2.close()

        dirlen = 2
        up.unpack(ziparc2.filename, self.outpath)

        unpack_len = len(os.listdir(self.outpath))

        assert unpack_len == dirlen

        shutil.rmtree(self.outpath)
        os.remove(os.path.join(curpath(), 'data', ziparc.filename))
        os.remove(os.path.join(curpath(), 'data', ziparc2.filename))

    def test_flatten(self):
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)
            os.makedirs(os.path.join(self.dirpath, 'dir1'))
            os.makedirs(os.path.join(self.dirpath, 'dir2'))
            self.fn1 = open(os.path.join(self.dirpath, 'dir1', 'fn1.txt'), 'a')
            self.fn2 = open(os.path.join(self.dirpath, 'dir1', 'fn2.txt'), 'a')
            self.fn3 = open(os.path.join(self.dirpath, 'dir2', 'fn3.txt'), 'a')
            self.fn1.close()
            self.fn2.close()
            self.fn3.close()

        dirlen = 3
        up.flatten(self.dirpath)

        flatten_len = len(os.listdir(self.dirpath))

        assert flatten_len == dirlen

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
