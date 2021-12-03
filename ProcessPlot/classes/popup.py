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

import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import re
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),  'Public')


class BaseSettingsPopoup(Gtk.Dialog):

  def __init__(self, parent, title):
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
    divider = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sc = divider.get_style_context()
    sc.add_class('Hdivider')
    self.dialog_window.pack_start(divider,0,0,1)
    self.content_area.add(self.dialog_window )
    self.build_base()
    self.show_all()



  def close_popup(self, button):
    self.destroy()

  def build_base(self):
    pass



class PenSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent):
      super().__init__(parent, "Pen Settings")

  def build_base(self):
    self.pen_grid = Gtk.Grid(column_homogeneous=True,column_spacing=10,row_spacing=10)
    self.content_area.add(self.pen_grid)
    labels = ['Chart Number', 'Connection', 'Tag', 'Visible', 'Lock Scale', 'Color',
          'Width', 'Scale Min', 'Scale Max', 'Auto Scale', 'Save'] # may want to create a table in the db for column names
    for l_idx in range(len(labels)):
        l = Gtk.Label(labels[l_idx])
        sc = l.get_style_context()
        sc.add_class('text-black-color')
        sc.add_class('font-14')
        sc.add_class('font-bold')
        self.pen_grid.attach(l, l_idx, 0, 1, 1)
    self.add_row('Add Data')

  def add_row(self,data,*args):

    self.pin_button = Gtk.Button(width_request = 20)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/settings.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.pin_button.add(image)
    sc = self.pin_button.get_style_context()
    sc.add_class('ctrl-button')
    self.pen_grid.attach(self.pin_button,0,1,1,1)



class PointSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent):
      super().__init__(parent, "Point Settings")


class ConnectionSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent):
      super().__init__(parent, "Connection Settings")