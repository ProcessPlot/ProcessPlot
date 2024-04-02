import os, logging 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Boolean
##$#from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import BIGINT, Float, Numeric


# see videosbelow for help:
# https://www.youtube.com/watch?v=jaKMm9njcJc&list=PL4iRawDSyRvVd1V7A45YtAGzDk6ljVPm1




SettingsBase = declarative_base()
class AppSettings(SettingsBase):
    __tablename__ = 'app_settings'
    id = Column(Integer, primary_key=True)
    last_save = Column(DateTime)
    headless = Column(Boolean)
    #other cols

class UiSettings(SettingsBase):
    __tablename__ = 'ui_settings'
    id = Column(Integer, primary_key=True)
    dark_mode = Column(Boolean)
    charts = Column(Integer)
    headless = Column(Boolean)
    screen_width = Column(Integer)
    screen_height = Column(Integer)
    #other cols

class ChartLayoutSettings(SettingsBase):
    __tablename__ = 'chart_layout_settings'
    id = Column(Integer, primary_key=True)
    cols = Column(Integer)
    rows = Column(Integer) 
    chart_map = Column(String) #save a list of the chart ids to place in each spot
    charts = Column(Integer)
    #other cols

class ChartSettings(SettingsBase):
    __tablename__ = 'chart_settings'
    id = Column(Integer, primary_key=True)
    bg_color = Column(String, default = '[1.0,1.0,1.0,1.0]') #rgb in json
    h_grids = Column(Integer, default = 3)
    v_grids = Column(Integer, default = 3)
    grid_color = Column(String, default = '[0.0,0.0,0.0,1.0]') #rgb in json
    marker1_width = Column(Integer, default = 1)
    marker1_color = Column(String, default = '[0.0,1.0,0.0,1.0]') #rgb in json    
    marker2_width = Column(Integer, default = 1)
    marker2_color = Column(String, default = '[1.0,0.0,0.0,1.0]') #rgb in json
    time_span = Column(Integer, default = 1)
    start_hour = Column(Integer, default = 1)
    start_minute = Column(Integer, default = 1)
    start_second = Column(Integer, default = 1)
    start_year = Column(Integer, default = 1)
    start_month = Column(Integer, default = 1)
    start_day = Column(Integer, default = 1)
    #other cols

class PenSettings(SettingsBase):
    __tablename__ = 'pen_settings'
    id = Column(Integer, primary_key=True)
    chart_id = Column(Integer,default=1)
    connection_id = Column(String)
    tag_id = Column(Integer)
    visible = Column(Boolean,default=1)
    color = Column(String, default = '#0000ff') #rgb in json
    weight = Column(String, default='1') # width
    scale_minimum = Column(String,default='0')
    scale_maximum = Column(String,default='100')
    scale_lock = Column(Boolean,default=0)
    scale_auto = Column(Boolean,default=0)
    #other cols

class SettingsDb():
    __log = logging.getLogger("ProcessPlot.classes.database")
    def __init__(self) -> None:
        super(SettingsDb, self).__init__()
        my_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(my_dir)
        engine = create_engine('sqlite:///'+ main_dir + "/settings/settings.db") #should create a .db file next to main.py
        self.models = {
            "app": AppSettings,
            "ui": UiSettings,
            "chart_layout": ChartLayoutSettings,
            "chart": ChartSettings,
            "pen": PenSettings,
        }
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.__log.debug('Opening database session for settings database')
        SettingsBase.metadata.create_all(engine) #creates all the tables above
        self.__log.debug(f"Database models created for settings database")

    def close(self):
        self.__log.debug('Closing settings database session')
        self.session.close()

ConnectionsBase = declarative_base()

class ConnectionTable(ConnectionsBase): # this table holds all tag values being subscribed to
  ##$#__tablename__ = 'connections'
  __tablename__ = 'connection-params-local'
  id = Column(Integer, primary_key=True)
  connection_type = Column(Integer, nullable=False)
  description = Column(String)

class ConnectionParamsModbusRTU(ConnectionsBase):
  __tablename__= 'connection-params-modbusRTU'
  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)
  pollrate = Column(Float, default=0.5)
  auto_connect = Column(Boolean, default=False)
  port = Column(String)
  station_id = Column(Integer, default=1)
  baudrate = Column(Integer, default=9600)
  timeout = Column(Float, default=3.0)
  stop_bit = Column(Integer, default=1)
  parity = Column(String, default='N')
  byte_size = Column(Integer, default=8)
  retries = Column(Integer, default=3)
  ##$#status = Column(Integer) #what is this?
  status = Column(Boolean, default=False)
  
class ConnectionParamsModbusTCP(ConnectionsBase):
  __tablename__= 'connection-params-modbusTCP'
  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)
  pollrate = Column(Float, default=0.5)
  auto_connect = Column(Boolean, default=False)
  host = Column(String, default='127.0.0.1')
  port = Column(Integer, default=502)
  station_id = Column(Integer, default=1)
  ##$#status = Column(Integer) #what is this?
  status = Column(Boolean, default=False)

class ConnectionParamsEthernetIP(ConnectionsBase):
  __tablename__= 'connection-params-ethernetIP'
  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)
  pollrate = Column(Float, default=0.5)
  auto_connect = Column(Boolean, default=False)
  host = Column(String, default='127.0.0.1') #uses pycomm3 syntax for PLC path
  port = Column(Integer, default=44818)
  ##$#status = Column(Integer) #what is this?
  status = Column(Boolean, default=False)

class ConnectionParamsOPC(ConnectionsBase):
  __tablename__= 'connection-params-opc'
  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)
  pollrate = Column(Float, default=0.5)
  auto_connect = Column(Boolean, default=False)
  host = Column(String, default='opc.tcp://127.0.0.1:49320') #uses pyopc url syntax for path
  ##$#status = Column(Integer) #what is this?
  status = Column(Boolean, default=False)

class ConnectionParamsGrbl(ConnectionsBase):
  __tablename__= 'connection-params-grbl'
  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)
  pollrate = Column(Float, default=0.5)
  auto_connect = Column(Boolean, default=False)
  port = Column(String, default='/dev/ttyACM0')
  ##$#status = Column(Integer) #what is this?
  status = Column(Boolean, default=False)

##$#class ConnectionParamsLocal(ConnectionsBase):
##$#  __tablename__= 'connection-params-local'
##$#  relationship('ConnectionTable', backref=backref('children', passive_deletes=True))
##$#  id = Column(String, ForeignKey(ConnectionTable.id, ondelete='CASCADE'), primary_key=True)

class TagTable(ConnectionsBase): # this table holds all tag values being subscribed to
  ##$#__tablename__ = 'tags'
  __tablename__ = 'tag-params-local'
  id = Column(String, primary_key=True) #tag unique id is a combo of tag and connection ids
  ##$#connection_id = Column(String, ForeignKey(ConnectionTable.id))
  connection_id = Column(String, ForeignKey(ConnectionTable.id), primary_key=True)
  description = Column(String)
  datatype = Column(String)
  value = Column(String) # used for retenitive tags

##$#class TagParamsLocal(ConnectionsBase):
##$#  __tablename__= 'tag-params-local'
##$#  relationship('TagTable', backref=backref('children', passive_deletes=True))
##$#  id = Column(String, ForeignKey(TagTable.id, ondelete='CASCADE'), primary_key=True)
##$#  address = Column(String, nullable=False)

class TagParamsEthernetIP(ConnectionsBase):
  ##$#__tablename__= 'tag-params-ethernetIP'
  __tablename__= 'tag-params-logix'
  relationship('TagTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(TagTable.id, ondelete='CASCADE'), primary_key=True)
  connection_id = Column(String, primary_key=True)
  __table_args__ = (ForeignKeyConstraint([id, connection_id],
                                          [TagTable.id, TagTable.connection_id], ondelete='CASCADE'),
                    {})
  address = Column(String, nullable=False)

class TagParamsModbus(ConnectionsBase):
  __tablename__= 'tag-params-modbus'
  relationship('TagTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(TagTable.id, ondelete='CASCADE'), primary_key=True)
  connection_id = Column(String, primary_key=True)
  __table_args__ = (ForeignKeyConstraint([id, connection_id],
                                          [TagTable.id, TagTable.connection_id], ondelete='CASCADE'),
                    {})
  address = Column(Integer, nullable=False)
  func_type = Column(Integer, nullable=False)
  bit = Column(Integer, default=0)
  word_swapped = Column(Boolean, default=False)
  byte_swapped = Column(Boolean, default=False)

class TagParamsOPC(ConnectionsBase):
  __tablename__= 'tag-params-opc'
  relationship('TagTable', backref=backref('children', passive_deletes=True))
  id = Column(String, ForeignKey(TagTable.id, ondelete='CASCADE'), primary_key=True)
  connection_id = Column(String, primary_key=True)
  __table_args__ = (ForeignKeyConstraint([id, connection_id],
                                          [TagTable.id, TagTable.connection_id], ondelete='CASCADE'),
                    {})
  node_id = Column(String, nullable=False)

class TagParamsGrbl(ConnectionsBase):
  __tablename__= 'tag-params-grbl'
  relationship('TagTable', backref=backref('children', passive_deletes=True))
  ##$#id = Column(String, ForeignKey(TagTable.id, ondelete='CASCADE'), primary_key=True)
  id = Column(String, primary_key=True)
  connection_id = Column(String, primary_key=True)
  __table_args__ = (ForeignKeyConstraint([id, connection_id],
                                          [TagTable.id, TagTable.connection_id], ondelete='CASCADE'),
                    {})
  address = Column(String, nullable=False)

class ConnectionsDb():
    __log = logging.getLogger("ProcessPlot.classes.database")
    def __init__(self) -> None:
        super(ConnectionsDb, self).__init__()
        my_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(my_dir)
        engine = create_engine('sqlite:///'+ main_dir + "/data/connections.db") #should create a .db file next to main.py
        self.models = {
                ##$#"connections": ConnectionTable,
                ##$#"connection-params-ethernetIP":  ConnectionParamsEthernetIP,
                "connection-params-logix":    ConnectionParamsEthernetIP,
                "connection-params-modbusRTU": ConnectionParamsModbusRTU,
                "connection-params-modbusTCP": ConnectionParamsModbusTCP,
                "connection-params-opc": ConnectionParamsOPC,
                "connection-params-grbl": ConnectionParamsGrbl,
                ##$#"connection-params-local": ConnectionParamsLocal,
                "connection-params-local": ConnectionTable,
                ##$#"tags": TagTable,
                "tag-params-local":  TagTable,
                ##$#"tag-params-local":  TagParamsLocal,
                "tag-params-ethernetIP":  TagParamsEthernetIP,
                "tag-params-modbus": TagParamsModbus,
                "tag-params-opc": TagParamsOPC,
                "tag-params-grbl": TagParamsGrbl
        }
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.__log.debug('Opening database session for connections database')
        ConnectionsBase.metadata.create_all(engine) #creates all the tables above
        self.__log.debug(f"Database models created for connections database")

    def close(self):
        self.__log.debug('Closing settings database session')
        self.session.close()

DataBase = declarative_base()
class Values(DataBase):
    __tablename__ = 'values'
    id = Column(Integer, primary_key=True)
    point_id = Column(Integer)
    timestamp = Column(DateTime)
    value = Column(Numeric)

class DataDb():
    __log = logging.getLogger("ProcessPlot.classes.database")
    def __init__(self) -> None:
        super(DataDb, self).__init__()
        my_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(my_dir)
        engine = create_engine('sqlite:///'+ main_dir + "/data/data.db") #should create a .db file next to main.py
        self.models = {
            "values": Values,
        }
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.__log.debug('Opening database session for data database')
        DataBase.metadata.create_all(engine) #creates all the tables above
        self.__log.debug(f"Database models created for data database")

    def close(self):
        self.__log.debug('Closing data database session')
        self.session.close()

