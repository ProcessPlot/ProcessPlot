"""
Copyright (c) 2021 Adam Solchenberger asolchenberger@gmail.com, Jason Engman engmanj@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio
from classes._version import __version__, __version_info__
from classes.logger import *
from classes.exceptions import *
from classes.chart import *
settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", False)


if len(sys.argv) > 1:
    lvl = {'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
    }
    if lvl.get(sys.argv[1]):
        configure_default_logger(level=lvl.get(sys.argv[1]), filename=sys.argv[2] if len(sys.argv) > 2 else None)
    

class Root(Gtk.Window):
  def __init__(self):
    title = 'Process Plot'
    Gtk.Window.__init__(self, title=title)
    self.set_size_request(100, 100)
    self.set_default_size(1920, 1000)
    self.set_border_width(10)
    self.big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    self.add(self.big_box)
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('ProcessPlot/Public/css/style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
    self.build_legend()
    self.build_chart()
    self.build_chart_ctrl()

  def build_chart(self,*args):
    trend_window = Gtk.Frame()
    trend_window.set_label("Trend Window")
    self.chart_panel = Gtk.Box()
    #self.build_panel.connect("button_release_event",self.build_panel_clicked)
    trend_window.add(self.chart_panel)
    self.charts = []
    for x in range(4):
      v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width=10)
      for y in range(4):
        c = Chart(y*4+x)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, border_width=10)
        box.pack_start(c, 1, 1, 0)
        self.charts.append(c)
        v_box.pack_start(box, 1, 1, 0)
      self.chart_panel.pack_start(v_box, 1, 1, 0)
    self.big_box.pack_start(trend_window,1,1,1)

  def build_legend(self):

    self.legend_window = Gtk.Box(width_request=400,orientation=Gtk.Orientation.VERTICAL)

    self.nav_button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=40,width_request=400)
    self.legend_window.pack_start(self.nav_button_bar,0,0,1)

    self.conn_button = Gtk.Button(width_request = 40)
    #self.conn_button.connect('clicked',self.setup_connection)
    #self.conn_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Connection.png', 40, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.conn_button.add(image)
    self.nav_button_bar.add(self.conn_button)
    sc = self.conn_button.get_style_context()
    sc.add_class('ctrl-button')

    self.tag_button = Gtk.Button(width_request = 40)
    #self.tag_button.connect('clicked',self.setup_tags,None)
    #self.tag_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Tag.png', 40, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.tag_button.add(image)
    self.nav_button_bar.add(self.tag_button)
    sc = self.tag_button.get_style_context()
    sc.add_class('ctrl-button')

    self.legend_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,width_request=400,height_request = 800)
    scroll = Gtk.ScrolledWindow()
    lbl = Gtk.Label(label = 'Legend Data')
    self.legend_data = Gtk.Box(width_request=400,orientation=Gtk.Orientation.VERTICAL)
    self.legend_data.pack_start(lbl,1,1,1)
    scroll.add(self.legend_data)
    self.legend_box.add(scroll)
    self.legend_window.pack_start(self.legend_box,1,1,1)

    self.big_box.pack_start(self.legend_window,0,0,1)

  def build_chart_ctrl(self):

    trend_control_panel = Gtk.Box(width_request=40,height_request=400,orientation=Gtk.Orientation.VERTICAL)
    self.pan_button = Gtk.Button(width_request = 30)
    #self.tag_button.connect('clicked',self.setup_tags,None)
    #self.tag_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/pan.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pan_button.add(image)
    trend_control_panel.add(self.pan_button)
    sc = self.pan_button.get_style_context()
    sc.add_class('ctrl-button')

    self.play_button = Gtk.Button(width_request = 30)
    #self.play_button.connect('clicked',self.setup_tags,None)
    #self.play_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/play.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.play_button.add(image)
    trend_control_panel.add(self.play_button)
    sc = self.play_button.get_style_context()
    sc.add_class('ctrl-button')

    self.stop_button = Gtk.Button(width_request = 30)
    #self.stop_button.connect('clicked',self.setup_tags,None)
    #self.stop_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/stop.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.stop_button.add(image)
    trend_control_panel.add(self.stop_button)
    sc = self.stop_button.get_style_context()
    sc.add_class('ctrl-button')
    
    self.big_box.pack_start(trend_control_panel,0,0,1)

  def exit_app(self, *args):
    Gtk.main_quit()

print(sys.argv)
win = Root()
win.connect("delete-event", win.exit_app)
win.show_all()
Gtk.main()

