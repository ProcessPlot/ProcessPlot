import logging, os, time
import gi
from ProcessLink.process_link import ProcessLink
from classes.ui import MainWindow
from classes.database import DataDb, SettingsDb, ConnectionsDb
from classes.ui import MainWindow
from classes.database_manager import DatabaseManager, DatabaseError

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),  'Public')

class App(object):
  __log = logging.getLogger('ProcessPlot.classes.app')
  def __init__(self):
    self.link = ProcessLink()
    self.link.set("db_file", "connections.db")
    self.link.load_db()
    
    self.data_db = DataDb()
    self.settings_db = SettingsDb()
    self.connections_db = ConnectionsDb()

    self.db = DatabaseManager()
    self.db.set("db_file", "connections.db")
    self.db.load_db()

    has_ui = True
    self.charts = {}
    self.charts_number = 0
    self.connection_type_enum ={
      1: "Local",
      2: "ModbusTCP_Connection",
      3: "ModbusRTU_Connection",
      4: "EthernetIP_Connection",
      5: "ADS_Connection",
      6: "Grbl_Connection",
      7: "OPCUA_Connection",
    }
    if has_ui:
      # build the UI and run the Gtk main loop
      self.main_window = MainWindow(self)
    else:
      self.__log.info("No UI, running headless")
      self.run_headless()

  def run_headless(self):
    print("Here is where you run command line version only")
    # simulate some main loop
    for x in range(5):
      print(f"No code written yet, closing in {5-x} second(s)")
      time.sleep(1)

  def load_db(self) -> bool:
    """
    load the settings db. return True if successful, else false
    if db is already loaded, this should close down the existing one first.
    this method only loads the db to the manager and gets the session
    ready. User is to call loading connections, tags, etc.
    """
    self.connections_db.db_file = self._db_file
    ##$#self.connections_db.open()
    session = self.connections_db.session
    orm = ConnectionsDb.models["connection-params-local"]
    conns = session.query(orm).all()
    print("CONNNNS",conns)
    # for conn in conns:
    #     params = CONNECTION_TYPES[conn.connection_type].get_params_from_db(session, conn.id)
    #     conn_obj = self.new_connection(params)
    #     conn_obj.load_tags_from_db(session)
    # return True

