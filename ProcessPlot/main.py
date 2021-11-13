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
from gi.repository import Gtk
from lib._version import __version__, __version_info__
from lib.logger import *
from lib.exceptions import *
from lib.chart import *
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
		self.charts = []
		for x in range(4):
			v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width=10)
			for y in range(4):
				c = Chart(y*4+x)
				box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, border_width=10)
				box.pack_start(c, 1, 1, 0)
				self.charts.append(c)
				v_box.pack_start(box, 1, 1, 0)
			self.big_box.pack_start(v_box, 1, 1, 0)

	def exit_app(self, *args):
		Gtk.main_quit()






print(sys.argv)
win = Root()
win.connect("delete-event", win.exit_app)
win.show_all()
Gtk.main()

