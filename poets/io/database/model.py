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
Created on May 20, 2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at

Contains the relational model classes of the accountancy database for SQLAlchemy
'''

import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from poets.settings import Database as dbconst
from poets.timedate.dateindex import dekad_index

engine = create_engine('postgresql://' + dbconst.user + ':' + dbconst.password
                       + '@' + dbconst.server + '/' + dbconst.database,
                       echo=False)

# Setup the declarative extension
Base = declarative_base(engine)


class Interface():
    '''
    Helper Class that connects to the database and provides meta queries that 
    do not fit into other objects.
    Attributes
    ----------
    session : sqlalchemy.orm.session.Session
        database session
    '''
    def __init__(self):
        pass

    def connect(self):
        '''
        Builds connection and populates sqlalchemy Classes
        '''
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def disconnect(self):
        '''
        Closes sqlalchemy session
        '''
        self.session.close()

    def get_gridpoints(self, country=None, poi=None):
        """
        returns gridpoints for defined grid

        Parameters
        ----------
        country : string
            FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)
        poi : integer
            Optional, gridpoint ID

        Returns
        -------
        points : pandas.DataFrame
            dataframe with longitude and latitude as values and gridpoint ID
            as index
        """
        point_id = []
        point_lon = []
        point_lat = []

        query = (self.session
                 .query(Grid,
                        Grid.id,
                        func.ST_X(func.ST_AsEWKT(Grid.geog)).label('lon'),
                        func.ST_Y(func.ST_AsEWKT(Grid.geog)).label('lat'))
                 .subquery())

        if poi != None:
            query = (self.session.query(query)
                     .filter(query.c.id == poi).subquery())

        query = self.session.query(query).order_by(query.c.id.asc()).all()

        for row in query:
            point_id.append(row.id)
            point_lon.append(row.lon)
            point_lat.append(row.lat)

        points = pd.DataFrame({'lon': point_lon, 'lat': point_lat}, point_id)

        return points

    def _create_date_index(self, begin, end=None):

        dtindex = dekad_index(begin, end)

        gridpoints = self.get_gridpoints().index

        for gpi in gridpoints:
            print 'Create dateindex for GP ' + str(gpi),
            for dt in dtindex:
                ds = Dataset()
                ds.gpi = gpi
                ds.time = dt
                self.session.add(ds)
            try:
                self.session.commit()
                print '[SUCCESS]'
            except:
                self.session.rollback()
                print '[ERROR]'


class Grid(Base):
    '''
    Grid class
    Attributes autoloaded from database
    '''
    __tablename__ = 'warp_grid'
    __table_args__ = {'autoload': True}


class Dataset(Base):
    """
    Dataset class
    Attributes autoloaded from database
    """
    __tablename__ = 'dataset'
    __table_args__ = {'autoload': True}


class Source(Base):
    '''
    Class for data sources
    Attributes autoloaded from database
    '''
    __tablename__ = 'warp_grid'
    __table_args__ = {'autoload': True}
