# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

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

'''
Created on May 21, 2014

@author: Thomas Mistlebauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from poets.constants import Database as dbconst

engine = create_engine('postgresql://' + dbconst.user + ':' + dbconst.password
                       + '@' + dbconst.server + '/' + dbconst.database,
                       echo=False)

# Setup the declarative extension
Base = declarative_base(engine)

create_postgis = 'CREATE EXTENSION postgis;'
create_schema = 'CREATE SCHEMA data;'
set_search_path = 'SET search_path TO data, public;'
create_dataset = ('CREATE TABLE dataset ('
                  'gpi integer REFERENCES warp_grid(id) PRIMARY KEY, '
                  'time timestamp without time zone NOT NULL, '
                  'UNIQUE (gpi, time));'
                  'CREATE INDEX gpi_index ON dataset USING btree(gpi);'
                  )

engine.execute(create_dataset)
