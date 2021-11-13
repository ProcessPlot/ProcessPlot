from OpenGL.GL import *
from OpenGL.GLU import *
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
from OpenGL.GL import *
from OpenGL.GL import shaders

fragment_shader ='''#version 150
        in vec4 color;
        out vec4 fColor;

        void main () {
            fColor = color;
        }'''
vertex_shader='''#version  150
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
        vert_shader = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
        frag_shader = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        self.overlay_shader_prog = shaders.compileProgram(vert_shader, frag_shader)


class Chart(Gtk.GLArea):
    def __init__(self, num):
        super(Chart, self).__init__()
        self.num = num
        self.context_realized = False
        self.context = None
        self.shaders = None
        self.vaos = []
        self.connect("realize", self.on_realize)
        self.connect("render", self.on_render)
        GObject.timeout_add(100, self.trigger_render)

    def on_realize(self, area):
        self.context_realized = True

    def on_render(self, area, ctx):
        print("Rendering....")
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


    def init_vaos(self):
        self.vaos = glGenVertexArrays(1)

    def render(self, *args):
        glClearColor(1.0/16.0 * self.num,0,1.0 - (1.0/16.0 * self.num),1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glFlush()

    def trigger_render(self, *args):
        self.queue_render()
        return True