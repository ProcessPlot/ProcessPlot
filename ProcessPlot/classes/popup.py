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
from Public.widgets.checkbox import CheckBoxWidget

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),  'Public')


class BaseSettingsPopoup(Gtk.Dialog):

  def __init__(self, parent, title,app):
    super().__init__(title=title, transient_for = parent,flags=0) 
    self.app = app
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

  def add_style(self, item,style):
    sc = item.get_style_context()
    for sty in style:
      sc.add_class(sty)

  def close_popup(self, button):
    self.destroy()

  def build_base(self):
    pass


class PenSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent,app):
    super().__init__(parent,"Pen Settings",app)

  def build_base(self):
    self.db_session = self.app.settings_db.session
    self.db_model = self.app.settings_db.models['pen']
    Tbl = self.db_model
    self.pen_row = 1
    self.pen_grid = Gtk.Grid(column_homogeneous=False,column_spacing=20,row_spacing=10)
    self.content_area.add(self.pen_grid)
    labels = ['Chart Number', 'Connection', 'Tag', 'Hide', 'Color',
          'Width', 'Scale Min', 'Scale Max', 'Auto Scale','Lock Scale','Save'] # may want to create a table in the db for column names
    for l_idx in range(len(labels)):
        l = Gtk.Label(labels[l_idx])
        sc = l.get_style_context()
        sc.add_class('text-black-color')
        sc.add_class('font-14')
        sc.add_class('font-bold')
        self.pen_grid.attach(l, l_idx, 0, 1, 1)
    settings = self.db_session.query(Tbl).order_by(Tbl.id)
    header = self.db_session.query(Tbl).first()
    c_name = header.__table__.columns
    params = {}
    column_names = []
    for col in c_name:
      column_names.append(str(col).split('.')[1])
    for pen in settings:
      #print(pen.connection_id)
      for c in column_names:
        params[c] = getattr(pen, c)
      row = Pen_row(params,self.pen_grid,self.pen_row)
      params.clear()
      self.pen_row += 1

################## Need to move Pen Row to widgets section
#################  Need to get save working
################   Need to add a chart filter drop down 
################   Need to get tags and connections list from database to fill drop downs
###############    Need an add pen row button

class Pen_row(object):
  def __init__(self,data,pen_grid,row,*args):
    self.row_data = data
    self.pen_grid = pen_grid
    self.pen_row = row
    self.build()
    #Rows start at 1 because row 0 is titles
    #Grid : Left,Top,Width,Height

  def build(self,*args):
    #Chart Select
    db_chart_number = str(self.row_data['chart_id'])
    selections = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
    self.chart_number = Gtk.ComboBoxText(width_request = 20)
    self.chart_number.set_entry_text_column(0)
    for x in selections:
        self.chart_number.append_text(x)
    try:
      idx = selections.index(str(db_chart_number))
    except IndexError:
      idx = 0
    sc = self.chart_number.get_style_context()
    sc.add_class('ctrl-combo')
    self.chart_number.set_active(idx)
    self.pen_grid.attach(self.chart_number,0,self.pen_row,1,1)
    self.chart_number.connect("changed", self.row_changed)

    #Connection Select
    db_conn_select = str(self.row_data['connection_id'])
    selections = ["Modbus"]
    self.conn_select = Gtk.ComboBoxText(width_request = 300)
    self.conn_select.set_entry_text_column(0)
    #self.number_of_charts.connect("changed", self.get_number_of_charts)
    for x in selections:
        self.conn_select.append_text(x)
    try:
      idx = selections.index(str(db_conn_select))
    except IndexError:
      idx = 0
    sc = self.conn_select.get_style_context()
    sc.add_class('ctrl-combo')
    self.conn_select.set_active(idx)
    self.pen_grid.attach(self.conn_select,1,self.pen_row,1,1)
    self.conn_select.connect("changed", self.row_changed)


    #Tag Select
    db_tag_select = str(self.row_data['tag_id'])
    selections = ["Field Current",'Speed']
    self.tag_select = Gtk.ComboBoxText(hexpand = True)
    self.tag_select.set_entry_text_column(0)
    #self.number_of_charts.connect("changed", self.get_number_of_charts)
    for x in selections:
        self.tag_select.append_text(x)
    try:
      idx = selections.index(str(db_tag_select))
    except IndexError:
      idx = 0
    self.tag_select.set_active(idx)
    sc = self.tag_select.get_style_context()
    sc.add_class('ctrl-combo')
    self.pen_grid.attach(self.tag_select,2,self.pen_row,1,1)
    self.tag_select.connect("changed", self.row_changed)

    #Display Status
    db_display_status = bool(self.row_data['visible'])
    box= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/Check.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    wid =CheckBoxWidget(30,30,image,db_display_status)
    self.display_status = wid.return_self()
    sc = self.display_status.get_style_context()
    sc.add_class('check-box')
    box.set_center_widget(self.display_status)
    self.pen_grid.attach(box,3,self.pen_row,1,1)
    self.display_status.connect("toggled", self.row_changed)

    #color
    db_color = str(self.row_data['color']) #example:#0000FF
    rgbcolor = Gdk.RGBA()
    rgbcolor.parse(db_color)
    rgbcolor.to_string()
    self.color_button = Gtk.ColorButton(width_request = 20)
    self.color_button.set_rgba (rgbcolor)
    sc = self.color_button.get_style_context()
    sc.add_class('ctrl-button')
    self.pen_grid.attach(self.color_button,4,self.pen_row,1,1)
    self.color_button.connect('color-set',self.row_changed)

    #line width
    db_line_width = str(self.row_data['weight']) 
    self.line_width = Gtk.Button(width_request = 20)
    lbl = Gtk.Label()
    lbl.set_label(db_line_width)
    self.add_style(lbl,['borderless-num-display','font-14','text-black-color'])
    self.line_width.add(lbl)
    sc = self.line_width.get_style_context()
    sc.add_class('ctrl-button')
    self.line_width.connect('clicked',self.open_numpad,lbl,{'min':0,'max':16,'type':int,'polarity':False})
    self.pen_grid.attach(self.line_width,5,self.pen_row,1,1)
    self.line_width.connect('clicked',self.row_changed)

    #scale minimum
    db_scale_minimum = str(self.row_data['scale_minimum']) 
    self.scale_minimum = Gtk.Button(width_request = 100)
    lbl = Gtk.Label()
    lbl.set_label(db_scale_minimum)
    self.add_style(lbl,['borderless-num-display','font-14','text-black-color'])
    self.scale_minimum.add(lbl)
    sc = self.scale_minimum.get_style_context()
    sc.add_class('ctrl-button')
    self.scale_minimum.connect('clicked',self.open_numpad,lbl,{'min':-32768,'max':32768,'type':float,'polarity':True})
    self.pen_grid.attach(self.scale_minimum,6,self.pen_row,1,1)
    self.scale_minimum.connect('clicked',self.row_changed)


    #scale maximum
    db_scale_maximum = str(self.row_data['scale_maximum']) 
    self.scale_maximum = Gtk.Button(width_request = 100)
    lbl = Gtk.Label()
    lbl.set_label(db_scale_maximum)
    self.add_style(lbl,['borderless-num-display','font-14','text-black-color'])
    self.scale_maximum.add(lbl)
    sc = self.scale_maximum.get_style_context()
    sc.add_class('ctrl-button')
    self.scale_maximum.connect('clicked',self.open_numpad,lbl,{'min':-32768,'max':32768,'type':float,'polarity':True})
    self.pen_grid.attach(self.scale_maximum,7,self.pen_row,1,1)
    self.scale_maximum.connect('clicked',self.row_changed)

    #Autoscale Status
    db_autoscale_status = bool(self.row_data['scale_auto'])
    box= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/Check.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    wid =CheckBoxWidget(30,30,image,db_autoscale_status)
    self.autoscale_status = wid.return_self()
    sc = self.autoscale_status.get_style_context()
    sc.add_class('check-box')
    box.set_center_widget(self.autoscale_status)
    self.pen_grid.attach(box,8,self.pen_row,1,1)
    self.autoscale_status.connect("toggled", self.row_changed)

    #Lockscale Status
    db_lockscale_status = bool(self.row_data['scale_lock'])
    box= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PUBLIC_DIR, 'images/Check.png'), 20, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    wid =CheckBoxWidget(30,30,image,db_lockscale_status)
    self.lockscale_status = wid.return_self()
    sc = self.lockscale_status.get_style_context()
    sc.add_class('check-box')
    box.set_center_widget(self.lockscale_status)
    self.pen_grid.attach(box,9,self.pen_row,1,1)
    self.lockscale_status.connect("toggled", self.row_changed)

    #Save Button
    self.save_button = Gtk.Button(width_request = 30)
    #self.pin_button.connect('clicked',self.close_popup)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./ProcessPlot/Public/images/Save.png', 30, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.save_button.add(image)
    sc = self.save_button.get_style_context()
    sc.add_class('ctrl-button')
    self.pen_grid.attach(self.save_button,10,self.pen_row,1,1)
    
  def open_numpad(self,button,widget_obj,params,*args):
    numpad = ValueEnter(self,widget_obj,params)
    response = numpad.run()
    if response == Gtk.ResponseType.NO:
      pass
    else:
      pass
      #callback(args)
    print(response)
    numpad.destroy()
  
  def row_changed(self,*args):
    self.add_style(self.save_button,['exit-button'])
  
  def add_style(self, item,style):
    sc = item.get_style_context()
    for items in sc.list_classes():
      #remove all default styles
      sc.remove_class(items)
    for sty in style:
      #add new styles
      sc.add_class(sty)


class PointSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent):
      super().__init__(parent, "Point Settings")


class ConnectionSettingsPopup(BaseSettingsPopoup):

  def __init__(self, parent):
      super().__init__(parent, "Connection Settings")


class ValueEnter(Gtk.Dialog):
  #Need to add check for value exceeding min,max range based on type
  def __init__(self, parent,obj,params):
    super().__init__(flags=0) 

    self.widget_obj = obj
    self.first_key_pressed = False #the user hasn't typed anything yet
    self.lbl = "Numpad"
    self.min = params['min']  #minimum value acceptable
    self.max = params['max']  #maximum value acceptable
    self.num_polarity = params['polarity']#whether value can be +/-
    self.num_type = params['type']  #whether number is int or float
    self.initial_value = 0
    self.set_default_size(600, 400)
    self.set_border_width(10)
    sc = self.get_style_context()
    sc.add_class("dialog-border")
    self.set_keep_above(True)
    self.set_decorated(False)
    self.content_area = self.get_content_area()

    self.dialog_window = Gtk.Box(width_request=600,orientation=Gtk.Orientation.VERTICAL)
    self.title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=20,width_request=600)

    #header
    title = Gtk.Label(label=self.lbl)
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
    #self.dialog_window.pack_start(divider,0,0,1)
    self.content_area.add(self.dialog_window )
    self.build_base()
    self.show_all()

  def build_base(self,*args):
    grid = Gtk.Grid(column_spacing=4, row_spacing=4, column_homogeneous=True, row_homogeneous=True,)
    pop_lbl = Gtk.Label("{}".format(self.lbl))
    self.add_style(pop_lbl,['borderless-num-display','font-14','text-black-color'])
    grid.attach(pop_lbl,0,0,2,1)
    self.dialog_window.pack_start(grid,1,1,1)
    sep = Gtk.Label(height_request=3)
    self.dialog_window.pack_start(sep,1,1,1)

    try:
      if isinstance(self.widget_obj, Gtk.Label):
        value = self.num_type(self.widget_obj.get_label())
      if isinstance(self.widget_obj, Gtk.Entry):
        value = self.num_type(self.widget_obj.get_text())
      self.initial_value = value
    except ValueError:
      value = 0

    #value = 0
    self.val_label = Gtk.Label(str(value))
    self.add_style(self.val_label,['numpad-display','font-16'])
    grid.attach(self.val_label,2,0,1,1)
    min_str = "-"+chr(0x221e) if type(self.min) == type(None) else self.min
    max_str = chr(0x221e) if type(self.max) == type(None) else self.max
    min_max_lbl = Gtk.Label(u"({} ~ {})".format(min_str, max_str))
    self.add_style(min_max_lbl,['font-14'])
    grid.attach(min_max_lbl,3,0,1,1)
    key = []
    for k in range(10):
      b = Gtk.Button(str(k), can_focus=False, can_default=False)
      #b.get_style_context().add_class("keypad_key")
      b.connect("clicked", self.btn_pressed)
      key.append(b)
      self.add_style(b,['numpad-bg','keypad_key'])
    grid.attach(key[7],0,2,1,1)
    grid.attach(key[8],1,2,1,1)
    grid.attach(key[9],2,2,1,1)
  
    grid.attach(key[4],0,3,1,1)
    grid.attach(key[5],1,3,1,1)
    grid.attach(key[6],2,3,1,1)

    grid.attach(key[1],0,4,1,1)
    grid.attach(key[2],1,4,1,1)
    grid.attach(key[3],2,4,1,1)

    grid.attach(key[0],0,5,2,1)

    period_key = Gtk.Button(".", can_focus=False, can_default=False)
    period_key.connect("clicked", self.add_period)
    self.add_style(period_key,['numpad-bg','keypad_key'])
    if self.num_type == float:
      grid.attach(period_key,2,5,1,1)

    PM_key = Gtk.Button("+/-")
    PM_key.connect("clicked", self.add_plus_minus)
    self.add_style(PM_key,['numpad-bg','keypad_key'])
    if self.num_polarity:
      grid.attach(PM_key,3,5,1,1)
    
    clear_key = Gtk.Button("CLEAR", can_focus=False, can_default=False)
    clear_key.connect("clicked", self.init_val)
    self.add_style(clear_key,['numpad-cmd-bg','keypad_enter'])
    grid.attach(clear_key,3,2,1,1)

    delete_key = Gtk.Button("DEL", can_focus=False, can_default=False)
    delete_key.connect("clicked", self.del_num)
    self.add_style(delete_key,['numpad-cmd-bg','keypad_enter'])
    grid.attach(delete_key,3,3,1,1)

    enter_key = Gtk.Button("ENTER", can_focus=False, can_default=False)
    enter_key.connect("clicked", self.accept_val)
    self.add_style(enter_key,['numpad-cmd-bg','keypad_enter'])
    grid.attach(enter_key,3,4,1,1)


    self.signals = []
    self.signals.append(self.connect('key-release-event', self.key_pressed))
    self.show_all()

    #Add style to dialog buttons
    a = self.get_action_area()
    b = a.get_children()
    for but in b:
      self.add_style(but,['dialog-buttons','font-16'])

  def key_pressed(self, popup, key_event):
    if key_event.get_keycode().keycode == 13:#Enter
      self.accept_val(None)
    if key_event.get_keycode().keycode == 8:#Backspace
      self.first_key_pressed = True #they want to use the number in there
      self.del_num(None)
    elif key_event.string == "-" or key_event.string == "+":
      self.add_plus_minus(None)
    elif key_event.string in "0123456789" and len(key_event.string)==1:
      self.update_val(key_event.string)
    elif key_event.string == ".":
      self.add_period(None)
    else:
      pass

  def add_style(self, item,style):
    sc = item.get_style_context()
    for sty in style:
      sc.add_class(sty)


  def btn_pressed(self, key):
    num = int(key.get_label())
    self.update_val(num)

  def update_val(self, num):
    if not self.first_key_pressed:
      val = str(num)
      self.first_key_pressed = True
    else:
      old_val = self.val_label.get_text()
      if old_val == '0':
        val = str(num)
      else:
        val = old_val+str(num)
    
    
    if self.check_limits(val):
      self.val_label.set_text(val)
  
  def check_limits(self, val):
    try:
      val = float(val)
    except ValueError:
      return False
    if not type(self.min) == type(None) and val < self.min:
      return False    
    if not type(self.max) == type(None) and val > self.max:
      return False
    return True
  
  def init_val(self, key):
    self.val_label.set_text('')
  
  def del_num(self,*args):
    val = self.val_label.get_text()
    val = (val)[:-1]
    if not val:
      val = '0'
    self.val_label.set_text(val)

  def add_period(self,*args):
    if not self.first_key_pressed:
      self.update_val("0")
    val = self.val_label.get_text()
    if "." not in val:
      val = val+"."
      self.val_label.set_text(val)

  def add_plus_minus(self,*args):
    val = self.val_label.get_text()
    if "-" not in val:
      val = "-"+val
    else:
      val = val.replace('-',"")
    if self.check_limits(val):
      self.val_label.set_text(val)

  def cleanup(self):
    for signal in self.signals:
      self.disconnect(signal)

  def accept_val(self, key):
    self.cleanup()
    try:
      if isinstance(self.widget_obj, Gtk.Label):
        self.widget_obj.set_label((self.val_label.get_text()))
        value = self.val_label.get_text()
      if isinstance(self.widget_obj, Gtk.Entry):
        self.widget_obj.set_text(str(self.val_label.get_text()))
        value = self.val_label.get_text()
      else:
        value = 0
    except ValueError:
      value = 0
      pass
    self.destroy()
    if str(self.initial_value) != str(value):
      pass
    else:
      pass

  def close_popup(self, button):
    self.destroy()