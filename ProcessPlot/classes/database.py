import os, logging 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.sqltypes import Numeric
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
    row = Column(Integer) 
    chart_map = Column(String) #save a list of the chart ids to place in each spot
    #other cols

class ChartSettings(Base):
    __tablename__ = 'chart_settings'
    id = Column(Integer, primary_key=True)
    bg_color = Column(DateTime)
    h_grids = Column(Integer)
    v_grids = Column(Integer)
    #other cols

class PenSettings(Base):
    __tablename__ = 'pen_settings'
    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)
    col_r = Column(Numeric)
    col_b = Column(Numeric)
    col_g = Column(Numeric)
    col_a = Column(Numeric)
    weight = Column(Numeric)

    #other cols



class Db():
    __log = logging.getLogger("classes.db")
    def __init__(self) -> None:
        super(Db, self).__init__()
        my_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(my_dir)
        self.engine = create_engine('sqlite:///'+ main_dir + "/settings.db") #should create a .db file next to main.py
        self.__log.info(f"db engine created - {self.engine}")
        self.models = {
            "app": AppSettings,
            "chart_layout": ChartLayoutSettings,
            "chart": ChartSettings,
            "pen": PenSettings,
        }
        for key, model in self.models.items():
            self.__log.debug(f'Creating db model {key}')
            model.metadata.create_all(self.engine)
            print(key)
         
    def get_db_model(self, tbl_name):
        return self.models.get(tbl_name)
