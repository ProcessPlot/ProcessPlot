import os, logging 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.sqltypes import Numeric


# see videosbelow for help:
# https://www.youtube.com/watch?v=jaKMm9njcJc&list=PL4iRawDSyRvVd1V7A45YtAGzDk6ljVPm1




Base = declarative_base()
class AppSettings(Base):
    __tablename__ = 'app_settings'
    id = Column(Integer, primary_key=True)
    last_save = Column(DateTime)
    charts = Column(Integer)
    #other cols

class ChartLayoutSettings(Base):
    __tablename__ = 'chart_layout_settings'
    id = Column(Integer, primary_key=True)
    cols = Column(Integer)
    rows = Column(Integer) 
    chart_map = Column(String) #save a list of the chart ids to place in each spot
    charts = Column(Integer)
    #other cols

class ChartSettings(Base):
    __tablename__ = 'chart_settings'
    id = Column(Integer, primary_key=True)
    bg_color = Column(String) #rgb in json
    h_grids = Column(Integer)
    v_grids = Column(Integer)
    #other cols

class PenSettings(Base):
    __tablename__ = 'pen_settings'
    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)
    color = Column(String) #rgb in json
    weight = Column(Numeric) # width

    #other cols



class Db():
    __log = logging.getLogger("classes.db")
    def __init__(self) -> None:
        super(Db, self).__init__()
        my_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(my_dir)
        engine = create_engine('sqlite:///'+ main_dir + "/settings.db") #should create a .db file next to main.py
        self.models = {
            "app": AppSettings,
            "chart_layout": ChartLayoutSettings,
            "chart": ChartSettings,
            "pen": PenSettings,
        }
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine) #creates all the tables above
        self.__log.info(f"Database models created")

