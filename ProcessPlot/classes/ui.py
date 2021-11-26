import logging, os
from typing import Set
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio

from classes.logger import *
from classes.chart import ChartArea
from classes.exceptions import *
from classes.chart import *
from classes.popup import PenSettingsPopup, ConnectionSettingsPopup, PointSettingsPopup

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),  'Public')

class MainWindow(Gtk.Window):
  __log = logging.getLogger('ProcessPlot.classes.ui')
  def __init__(self, app):
    self.app  = app
    self.db_session = app.settings_db.session
    self.db_model = app.settings_db.models['ui']
    #settings
    self.numCharts = 1
    self.dark_mode = False
    #settings
    self.load_settings()
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", self.dark_mode)
    title = 'Process Plot'
    Gtk.Window.__init__(self, title=title)
    self.connect("delete-event", self.exit_app)
    self.set_size_request(100, 100)
    self.set_default_size(1950, 1050)
    self.set_border_width(10)
    self.set_decorated(False)
    self.maximize()
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path(os.path.join(PUBLIC_DIR, 'css/style.css'))
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
    self.window = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.settings_popout= Gtk.Box(orientation=Gtk.Orientation.VERTICAL, width_request = 0)
    self.big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    self.titlebar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 20)
    self.add(self.window)
    self.window.pack_start(self.titlebar,0,0,1)
    self.window.pack_start(self.big_box,1,1,1)
    self.big_box.pack_start(self.settings_popout,0,0,1)
    #building trend window 
    self.trend_window = Gtk.EventBox()
    self.trend_window.set_above_child(True)
    sc = self.trend_window.get_style_context()
    sc.add_class('dialog-border')
    self.trend_window.connect("button_release_event",self.event_window_clicked)
    self.big_box.pack_start(self.trend_window,1,1,1)
    #adding widgets
    self.build_chart()
    self.build_titlebar()
    self.build_chart_ctrl()
    self.show_all()
    Gtk.main()

  def load_settings(self):
    Tbl = self.db_model
    settings = self.db_session.query(Tbl).order_by(Tbl.id.asc()).first() # find the latest id
    if settings:
      self.dark_mode = settings.dark_mode
      self.numCharts = settings.charts

  def save_settings(self):
    Tbl = self.db_model
    settings = self.db_session.query(Tbl).order_by(Tbl.id.asc()).first() # find the latest id
    if settings:
      settings.dark_mode = self.dark_mode
      settings.charts = self.numCharts
    else:
      self.db_session.add(Tbl(dark_mode=self.dark_mode, charts=self.numCharts))
    self.db_session.commit()

  
  def build_titlebar(self,*args):

    sc = self.titlebar.get_style_context()
    sc.add_class('title-bar')

    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.build_settings_popout)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/settings.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.titlebar.pack_start(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('ctrl-button')

    selections = ["1","2","4","8","16"]
    self.number_of_charts = Gtk.ComboBoxText()
    self.number_of_charts.set_entry_text_column(0)
    self.number_of_charts.connect("changed", self.update_number_of_charts)
    found = 0
    for x in selections:
        self.number_of_charts.append_text(x)
    try:
      idx = selections.index(str(self.numCharts))
    except IndexError:
      idx = 0
    self.number_of_charts.set_active(idx)
    self.titlebar.pack_start(self.number_of_charts,0,0,1)

    title = Gtk.Label(label = 'ProcessPlot')
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.titlebar.pack_start(title,1,1,1)

    self.exit_button = Gtk.Button(width_request = 15)
    self.exit_button.connect('clicked',self.exit_app)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/Close.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.exit_button.add(image)
    self.titlebar.pack_start(self.exit_button,0,0,1)
    sc = self.exit_button.get_style_context()
    sc.add_class('exit-button')

  def update_number_of_charts(self,chart_select):
    self.chart_panel.charts = self.numCharts = int(chart_select.get_active_text())
    self.chart_panel.build_charts()
    self.save_settings()

  def build_settings_popout(self,*args):

    self.settings_window = Gtk.Box(width_request=300,orientation=Gtk.Orientation.VERTICAL)
    self.settings_title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=20,width_request=300)

    self.popups = {
      "pen": PenSettingsPopup,
      "point": PointSettingsPopup,
      "connection": ConnectionSettingsPopup,
    }

    #header
    title = Gtk.Label(label = 'Settings')
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.settings_title_bar.pack_start(title,1,1,1)
    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.remove_settings_popout)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/pin.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.settings_title_bar.pack_start(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('ctrl-button')
    self.settings_window.pack_start(self.settings_title_bar,0,0,1)

    self.ctrl_button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=30,width_request=300)

    self.conn_button = Gtk.Button(width_request = 30)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Connection.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.conn_button.add(image)
    self.ctrl_button_bar.add(self.conn_button)
    sc = self.conn_button.get_style_context()
    sc.add_class('ctrl-button')
    self.conn_button.connect('clicked',self.open_popup,"connection")

    self.point_button = Gtk.Button(width_request = 30)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Tag.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.point_button.add(image)
    self.ctrl_button_bar.add(self.point_button)
    sc = self.point_button.get_style_context()
    sc.add_class('ctrl-button')
    self.point_button.connect('clicked',self.open_popup,"point")
 
    self.pen_settings_button = Gtk.Button(width_request = 30)

    self.pen_settings_button.connect('clicked',self.open_popup,"pen")
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Create.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pen_settings_button.add(image)
    self.ctrl_button_bar.add(self.pen_settings_button)
    sc = self.pen_settings_button.get_style_context()
    sc.add_class('ctrl-button')

    self.settings_window.pack_start(self.ctrl_button_bar,0,0,1)

    #Settings Data

    self.settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,width_request=300,height_request = 800)
    scroll = Gtk.ScrolledWindow()
    lbl = Gtk.Label(label = 'Settings')
    self.settings_data = Gtk.Box(width_request=300,orientation=Gtk.Orientation.VERTICAL)
    self.settings_data.pack_start(lbl,1,1,1)
    scroll.add(self.settings_data)
    self.settings_box.add(scroll)
    self.settings_window.pack_start(self.settings_box,1,1,1)
    
    self.settings_popout.pack_start(self.settings_window,1,1,1)
    self.big_box.show_all()
  
  def remove_settings_popout(self,*args):
    wid = self.settings_popout.get_children()
    for item in wid:
      self.settings_popout.remove(item)
    self.big_box.show_all()
  
  def build_chart(self,*args):
    self.chart_panel = ChartArea(self.app)
    self.trend_window.add(self.chart_panel)
    self.big_box.show_all()

  def build_chart_ctrl(self):
    trend_control_panel = Gtk.Box(width_request=40,height_request=400,orientation=Gtk.Orientation.VERTICAL)
    self.pan_button = Gtk.Button(width_request = 30)
    self.pan_button.connect('clicked',self.exit_app,None)
    #self.pan_button.connect('clicked',self.setup_tags,None)
    #self.pan_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR,'images/pan.png'), 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pan_button.add(image)
    trend_control_panel.add(self.pan_button)
    sc = self.pan_button.get_style_context()
    sc.add_class('ctrl-button')

    self.play_button = Gtk.Button(width_request = 30)
    #self.play_button.connect('clicked',self.setup_tags,None)
    #self.play_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR,'images/play.png'), 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.play_button.add(image)
    trend_control_panel.add(self.play_button)
    sc = self.play_button.get_style_context()
    sc.add_class('ctrl-button')

    self.stop_button = Gtk.Button(width_request = 30)
    #self.stop_button.connect('clicked',self.setup_tags,None)
    #self.stop_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/stop.png'), 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.stop_button.add(image)
    trend_control_panel.add(self.stop_button)
    sc = self.stop_button.get_style_context()
    sc.add_class('ctrl-button')
    
    self.big_box.pack_start(trend_control_panel,0,0,1)
 
  def open_popup(self, button,popup_key):
    popup = self.popups[popup_key](self)
    response = popup.run()
    popup.destroy()

  def exit_app(self, *args):
    Gtk.main_quit()

  def event_window_clicked(self,*args):
    self.__log.info(f'Event window clicked')
