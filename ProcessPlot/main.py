import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from shaders import Chart
settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", False)



class Root(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Process Plot')
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







win = Root()
win.connect("delete-event", win.exit_app)
win.show_all()
Gtk.main()

