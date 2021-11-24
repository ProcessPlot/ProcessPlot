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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import re

class LegendPopup(Gtk.Dialog):


  def __init__(self, parent):
    super().__init__(title="My Dialog", flags=0)
    self.parent = parent
    self.set_default_size(300, 1000)
    self.move(0,85)
    self.set_decorated(False)
    self.set_border_width(10)
    self.set_keep_above(False)
    sc = self.get_style_context()
    sc.add_class("dialog-border")
    self.content_area = self.get_content_area()

    self.legend_window = Gtk.Box(width_request=300,orientation=Gtk.Orientation.VERTICAL)
    self.legend_title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=20,width_request=300)

    #header
    title = Gtk.Label(label = 'Legend')
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.legend_title_bar.pack_start(title,1,1,1)
    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.close_legend_popup)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/pin.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.legend_title_bar.pack_start(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('ctrl-button')
    self.legend_window.pack_start(self.legend_title_bar,0,0,1)

    #control button bar
    self.popups = {
      "pen": PenSettingsPopup,
      "point": PointSettingsPopup,
      "connection": ConnectionSettingsPopup,
    }
    self.ctrl_button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=30,width_request=300)

    self.conn_button = Gtk.Button(width_request = 30)
    #self.conn_button.connect('clicked',self.open_legend_popup)
    #self.conn_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Connection.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.conn_button.add(image)
    self.ctrl_button_bar.add(self.conn_button)
    sc = self.conn_button.get_style_context()
    sc.add_class('ctrl-button')
    self.conn_button.connect('clicked',self.open_popup,"connection", self.parent)

    self.point_button = Gtk.Button(width_request = 30)
    #self.point_button.connect('clicked',self.setup_tags,None)
    #self.point_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Tag.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.point_button.add(image)
    self.ctrl_button_bar.add(self.point_button)
    sc = self.point_button.get_style_context()
    sc.add_class('ctrl-button')
    self.point_button.connect('clicked',self.open_popup,"point", self.parent)
 
    self.pen_settings_button = Gtk.Button(width_request = 30)

    self.pen_settings_button.connect('clicked',self.open_popup,"pen", self.parent)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Create.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pen_settings_button.add(image)
    self.ctrl_button_bar.add(self.pen_settings_button)
    sc = self.pen_settings_button.get_style_context()
    sc.add_class('ctrl-button')

    self.legend_window.pack_start(self.ctrl_button_bar,0,0,1)

    #legend data

    self.legend_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,width_request=300,height_request = 800)
    scroll = Gtk.ScrolledWindow()
    lbl = Gtk.Label(label = 'Legend Data')
    self.legend_data = Gtk.Box(width_request=300,orientation=Gtk.Orientation.VERTICAL)
    self.legend_data.pack_start(lbl,1,1,1)
    scroll.add(self.legend_data)
    self.legend_box.add(scroll)
    self.legend_window.pack_start(self.legend_box,1,1,1)
    
    self.content_area.add(self.legend_window)
    self.show_all()

  def close_legend_popup(self, button):
    self.destroy()

  def build_base(self):
    pass

  def open_popup(self, button,popup_key, parent):
    popup = self.popups[popup_key](self,parent)
    response = popup.run()
    popup.destroy()

class SettingsPopup(Gtk.Dialog):

  def __init__(self, parent):
    super().__init__(title="App Settings", transient_for = parent,flags=0)
      
    self.set_default_size(600, 600)
    self.set_decorated(False)
    self.set_border_width(10)
    self.set_keep_above(False)
    sc = self.get_style_context()
    sc.add_class("dialog-border")
    self.content_area = self.get_content_area()

    self.dialog_window = Gtk.Box(width_request=600,orientation=Gtk.Orientation.VERTICAL)
    self.title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=20,width_request=600)

    #header
    title = Gtk.Label(label = 'App Settings')
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.title_bar.pack_start(title,1,1,1)
    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.close_popup)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Close.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.title_bar.pack_end(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('exit-button')
    self.dialog_window.pack_start(self.title_bar,0,0,1)

    self.content_area.add(self.dialog_window )
    self.show_all()



  def close_popup(self, button):
    self.destroy()

  def build_base(self):
    pass



class BaseSettingsPopoup(Gtk.Dialog):

  def __init__(self, obj,parent, title):
    super().__init__(title=title, transient_for = parent,flags=0)  
    self.set_default_size(1500, 700)
    self.set_decorated(False)
    self.set_border_width(10)
    self.set_keep_above(False)
    sc = self.get_style_context()
    sc.add_class("dialog-border")
    self.content_area = self.get_content_area()

    self.dialog_window = Gtk.Box(width_request=600,orientation=Gtk.Orientation.VERTICAL)
    self.title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=20,width_request=600)

    #header
    title = Gtk.Label(label=title)
    sc = title.get_style_context()
    sc.add_class('text-black-color')
    sc.add_class('font-18')
    sc.add_class('font-bold')
    self.title_bar.pack_start(title,1,1,1)
    self.pin_button = Gtk.Button(width_request = 20)
    self.pin_button.connect('clicked',self.close_popup)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Close.png', 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    self.title_bar.pack_end(self.pin_button,0,0,1)
    sc = self.pin_button.get_style_context()
    sc.add_class('exit-button')
    self.dialog_window.pack_start(self.title_bar,0,0,1)

    self.content_area.add(self.dialog_window )
    self.show_all()



  def close_popup(self, button):
    self.destroy()

  def build_base(self):
    pass




class PenSettingsPopup(BaseSettingsPopoup):

  def __init__(self, obj, parent):
      super().__init__(obj, parent, "Pen Settings")


class PointSettingsPopup(BaseSettingsPopoup):

  def __init__(self, obj, parent):
      super().__init__(obj, parent, "Point Settings")


class ConnectionSettingsPopup(BaseSettingsPopoup):

  def __init__(self, obj, parent):
      super().__init__(obj, parent, "Connection Settings")