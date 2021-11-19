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

from OpenGL.GL import *
from OpenGL.GLU import *
import logging
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from OpenGL.GL import *
from OpenGL.GL import shaders
from sqlalchemy import select as sql_select
import json

__all__ = ['Chart']


FRAG_SHADER ='''#version 150
        in vec4 color;
        out vec4 fColor;

        void main () {
            fColor = color;
        }'''

VERT_SHADER='''#version  150
in vec2 vert;
in vec4 in_color;
out vec4 color;
void main () {
    color = in_color;
    gl_Position = vec4(vert, -.99f, 1.0f);
}'''


class Shaders(GObject.Object):
    '''do not instantiate if context is not current'''

    def __init__(self):
        super(Shaders, self).__init__()
        self.compile_shaders()


    def compile_shaders(self):
        vert_shader = shaders.compileShader(VERT_SHADER, GL_VERTEX_SHADER)
        frag_shader = shaders.compileShader(FRAG_SHADER, GL_FRAGMENT_SHADER)
        self.overlay_shader_prog = shaders.compileProgram(vert_shader, frag_shader)
        


class Chart(Gtk.GLArea):
    __log = logging.getLogger("ProcessPlot.classes.Chart")

    def __init__(self, root, db_id=None):
        super(Chart, self).__init__()
        self.root = root
        self.db_id = db_id # None means it's new and isn't to be looked up in the db, if saved, gets an id.
        self.db_model = root.db.models['chart']
        self.db_session = root.db.session
        #settings
        self.bg_color = (0.9, 0.1, 0.1, 1.0)
        self.h_grids = 0
        self.v_grids = 0
        #settings
        self.load_settings()
        self.context_realized = False
        self.context = None
        self.shaders = None
        self.vaos = []
        self.connect("realize", self.on_realize)
        self.connect("render", self.on_render)
        GObject.timeout_add(100, self.trigger_render)


    def on_realize(self, area):
        self.context_realized = True
        self.__log.info(f"GL Context Realized - {self}")

    def on_render(self, area, ctx):
        #self.__log.debug("Rendering....")
        if self.context == ctx == None:
            return
        elif self.context == None and ctx != None:
            self.context = ctx
            try:
                self.shaders = Shaders()
            except RuntimeError:
                print('OpenGL Error - Data logging only')
                self.shaders = None
            if self.shaders:
                self.init_vaos()
        if self.shaders:
            self.render()
    
    def load_settings(self):
        if not self.db_id:
            return
        tbl = self.db_model
        settings = self.db_session.query(tbl).filter(tbl.id == self.db_id).first() # find one with this id
        if settings:
            self.bg_color = json.loads(settings.bg_color) #rgb in json
            self.h_grids = settings.h_grids
            self.v_grids = settings.v_grids

    
    def save_settings(self):
        tbl = self.db_model
        entry = None
        if self.db_id:
            entry = self.db_session.query(tbl).filter(tbl.id==self.db_id).first()
        if entry: # update it
            entry.bg_color = json.dumps(self.bg_color)
            entry.h_grids= self.h_grids
            entry.v_grids=self.v_grids
        else: #create it
            entry = tbl(
                bg_color = json.dumps(self.bg_color),
                h_grids= self.h_grids,
                v_grids=self.v_grids
            )
            self.db_session.add(entry)
        # or 
        # entry1 = model(bla= "blah")
        # entry2 = model(bla= "blah, blah")
        # self.db_session.add_all([entry1, entry2])
        self.db_session.commit()
        self.db_id = entry.id
        



    def init_vaos(self):
        self.vaos = glGenVertexArrays(1)

    def render(self, *args):
        glClearColor(*self.bg_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glFlush()

    def trigger_render(self, *args):
        self.queue_render()
        return True


class ChartArea(Gtk.Box):
    __log = logging.getLogger("ProcessPlot.classes.ChartArea")
    def __init__(self, root, db_id=None):
        super(ChartArea, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=40)
        self.root = root
        #settings
        self.cols = 1
        self.rows = 1
        self.chart_map = '[1]' # json list(rows) of lists(cols) that map ids of charts to row 
        #settings
        self.db_model = self.root.db.models['chart_layout']
        self.db_session = root.db.session
        self.load_settings()
        top_pane = Gtk.Paned(wide_handle=True)
        top_pane.pack1(Chart(root,1),1,1)
        top_pane.pack2(Chart(root,2),1,1)
        top_box = Gtk.Box()
        top_box.pack_start(top_pane,1,1,1)
        bot_pane = Gtk.Paned(wide_handle=True)
        bot_pane.pack1(Chart(root,3),1,1)
        bot_pane.pack2(Chart(root,4),1,1)
        bot_box = Gtk.Box()
        bot_box.pack_start(bot_pane,1,1,1)


        v_pane = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL, wide_handle=True)
        v_pane.set_property("position", 100)
        v_pane.pack1(top_box,1,1)
        v_pane.pack2(bot_box,1,1)
        self.pack_start(v_pane,1,1,1)
        self.__log.info(f"ChartArea built - {self}")
    
    def load_settings(self):
        settings = self.db_session.query(self.db_model).order_by(self.db_model.id.desc()).first() # last one saved?
        if settings:
            self.rows = settings.rows
            self.cols = settings.cols
            self.chart_map = settings.chart_map

    
    def save_settings(self):
        entry = self.db_model(
            cols = self.cols,
            rows = self.rows,
            chart_map = self.chart_map
        )
        self.db_session.add(entry)
        # or 
        # entry1 = model(bla= "blah")
        # entry2 = model(bla= "blah, blah")
        # self.db_session.add_all([entry1, entry2])
        self.db_session.commit()


