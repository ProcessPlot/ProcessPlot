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

from classes.chart import ChartArea

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio
from classes._version import __version__, __version_info__
from classes.logger import *
from classes.exceptions import *
from classes.chart import *
from classes.popup import LegendPopup
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

  __log = logging.getLogger("ProcessPlot.Root")
  def __init__(self):
    title = 'Process Plot'
    Gtk.Window.__init__(self, title=title)
    self.set_size_request(100, 100)
    self.set_default_size(1950, 1050)
    self.set_border_width(10)
    self.set_decorated(False)
    self.maximize()
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('ProcessPlot/Public/css/style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
    self.window = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    self.titlebar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 20)
    self.add(self.window)
    self.window.pack_start(self.titlebar,0,0,1)
    self.window.pack_start(self.big_box,1,1,1)
    self.build_titlebar()
    self.build_chart()
    self.build_chart_ctrl()

  def build_titlebar(self,*args):

    sc = self.titlebar.get_style_context()
    sc.add_class('title-bar')

    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.open_legend_popup)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/legend.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.titlebar.pack_start(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('ctrl-button')

    title = Gtk.Label(label = 'ProcessPlot')
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.titlebar.pack_start(title,1,1,1)

    self.exit_button = Gtk.Button(width_request = 15)
    self.exit_button.connect('clicked',self.exit_app)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Close.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.exit_button.add(image)
    self.titlebar.pack_start(self.exit_button,0,0,1)
    sc = self.exit_button.get_style_context()
    sc.add_class('exit-button')

  def build_chart(self,*args):

    self.trend_window = Gtk.EventBox()
    self.trend_window.set_above_child(False) # need below or the panes won't resize
    sc = self.trend_window.get_style_context()
    sc.add_class('dialog-border')
    self.trend_window.connect("button_release_event",self.event_window_clicked)    
    self.chart_panel = ChartArea()
    self.trend_window.add(self.chart_panel)
    self.big_box.pack_start(self.trend_window,1,1,1)

  def build_chart_ctrl(self):

    trend_control_panel = Gtk.Box(width_request=40,height_request=400,orientation=Gtk.Orientation.VERTICAL)
    self.pan_button = Gtk.Button(width_request = 30)
    self.pan_button.connect('clicked',self.exit_app,None)
    #self.pan_button.connect('clicked',self.setup_tags,None)
    #self.pan_button.set_sensitive(False)
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

  def open_legend_popup(self, button):
    popup = LegendPopup(self)
    response = popup.run()
    popup.destroy()

  def exit_app(self, *args):
    Gtk.main_quit()

  def event_window_clicked(self,*args):
    self.__log.debug(f"click event recieved {args}")

__log = logging.getLogger("ProcessPlot.main")
__log.info(f"CLI arguments - {sys.argv}")
win = Root()
win.connect("delete-event", win.exit_app)
win.show_all()
Gtk.main()

