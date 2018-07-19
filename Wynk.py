#!/usr/bin/python

import gobject
import gtk
import collections
import math

COLOR_WINDOW_BACKGROUND = gtk.gdk.Color('#0c0c14')
COLOR_WIDGET_BACKGROUND = gtk.gdk.Color('#0c0c14')
COLOR_WIDGET_FOREGROUND = gtk.gdk.Color('#27292d')
COLOR_WIDGET_TITLE = gtk.gdk.Color('#828282')
COLOR_WIDGET_VALUE = gtk.gdk.Color('#df9524')

GRID_LENGTH = 80
GRID_HEIGHT = 60


class ValueDisplay(gtk.DrawingArea):
    def __init__(self, param, value=0.0):
        gtk.DrawingArea.__init__(self)
        self.connect('expose-event', self.expose)
        self.set_size_request(GRID_LENGTH, GRID_HEIGHT)
        self.param = param
        self.value = None
        self.set_value(value)
        self.modify_bg(gtk.STATE_NORMAL, COLOR_WIDGET_BACKGROUND)

    def set_value(self, value):
        self.value = str(value)

    def expose(self, widget, event):
        cairo = widget.window.cairo_create()

        cairo.set_source_rgb(
            float(COLOR_WIDGET_FOREGROUND.red) / 65535,
            float(COLOR_WIDGET_FOREGROUND.green) / 65535,
            float(COLOR_WIDGET_FOREGROUND.blue) / 65535)
        cairo.rectangle(1, 1, GRID_LENGTH - 2, GRID_HEIGHT - 2)
        cairo.fill()

        cairo.set_source_rgb(
            float(COLOR_WIDGET_TITLE.red) / 65535,
            float(COLOR_WIDGET_TITLE.green) / 65535,
            float(COLOR_WIDGET_TITLE.blue) / 65535)
        cairo.select_font_face("Helvetica")
        cairo.set_font_size(12)
        cairo.move_to(5, 15)
        cairo.show_text(self.param)

        cairo.set_source_rgb(
            float(COLOR_WIDGET_VALUE.red) / 65535,
            float(COLOR_WIDGET_VALUE.green) / 65535,
            float(COLOR_WIDGET_VALUE.blue) / 65535)
        cairo.select_font_face("Helvetica")
        cairo.set_font_size(24)
        cairo.move_to(5, GRID_HEIGHT * 0.80)
        cairo.show_text(self.value)

    def repaint(self):
        self.queue_draw()


class ElementRectangle():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def render(self, cairo):
        cairo.set_source_rgb(0.5, 0.5, 0.5)
        cairo.rectangle(self.x - (self.w / 2.0), self.y - (self.h / 2.0), self.w, self.h)
        cairo.fill()


class ElementCircle():
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def render(self, cairo):
        cairo.set_source_rgb(0.5, 0.5, 0.5)
        cairo.arc(self.x, self.y, self.r, 0, 2 * math.pi)
        cairo.fill()


class ElementLineSeries():
    def __init__(self, samples_x, samples_y):
        self.samples_x = samples_x
        self.samples_y = samples_y

    def render(self, cairo):
        cairo.set_source_rgb(0.5, 0.5, 0.5)
        cairo.set_line_width(1)
        cairo.move_to(self.samples_x[0], self.samples_y[0])
        for i in range(1, len(self.samples_x) - 1):
            cairo.rel_line_to(self.samples_x[i], self.samples_y[i])
            cairo.move_to(self.samples_x[i], self.samples_y[i])
            print i, self.samples_x[i], self.samples_y[i]
        cairo.stroke()


class Canvas(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.connect('expose-event', self.expose)
        self.elements = collections.defaultdict()

    def get_elements(self):
        return self.elements

    def add_element(self, name, element):
        self.elements[name] = element

    def remove_element(self, name):
        self.elements.pop(name)

    def remove_all_elements(self):
        self.elements.clear()

    def expose(self, widget, event):
        cairo = widget.window.cairo_create()
        for k,v in self.elements.iteritems():
            v.render(cairo)

    def repaint(self):
        self.queue_draw()


class Display(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title('Wynk Demo')
        self.set_size_request(GRID_LENGTH * 4, GRID_HEIGHT * 8)
        self.set_position(gtk.WIN_POS_NONE)
        self.modify_bg(gtk.STATE_NORMAL, COLOR_WINDOW_BACKGROUND)
        self.connect('destroy', gtk.main_quit)
        self.fixed = gtk.Fixed()
        self.add(self.fixed)

        v = ValueDisplay('HOTDOGS')
        self.fixed.put(v, GRID_LENGTH * 0, GRID_HEIGHT * 0)

        v = ValueDisplay('HOTDOGS')
        self.fixed.put(v, GRID_LENGTH * 1, GRID_HEIGHT * 0)

        v = ValueDisplay('HOTDOGS')
        self.fixed.put(v, GRID_LENGTH * 2, GRID_HEIGHT * 0)

        v = ValueDisplay('HOTDOGS')
        self.fixed.put(v, GRID_LENGTH * 3, GRID_HEIGHT * 0)
        v.set_value(33.45)

        self.set_resizable(False)
        self.show_all()


Display()

gtk.main()