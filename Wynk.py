#!/usr/bin/python

import gtk

COLOR_WINDOW_BACKGROUND = gtk.gdk.Color('#0c0c14')
COLOR_WIDGET_BACKGROUND = gtk.gdk.Color('#0c0c14')
COLOR_WIDGET_FOREGROUND = gtk.gdk.Color('#27292d')
COLOR_WIDGET_TITLE = gtk.gdk.Color('#828282')
COLOR_WIDGET_VALUE = gtk.gdk.Color('#df9524')
COLOR_WIDGET_ON = gtk.gdk.Color('#00ff00')
COLOR_WIDGET_OFF = gtk.gdk.Color('#ff0000')
COLOR_WIDGET_TOGGLE = gtk.gdk.Color('#444444')

GRID_LENGTH = 80
GRID_HEIGHT = 60


def set_cairo_color(cairo, color):
    cairo.set_source_rgb(
        float(color.red) / 65535,
        float(color.green) / 65535,
        float(color.blue) / 65535)


class Widget(gtk.DrawingArea):
    def __init__(self, grid_cols=1, grid_rows=1):
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_click)
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.connect('expose-event', self.expose)
        self.set_size_request(self.grid_cols * GRID_LENGTH, self.grid_rows * GRID_HEIGHT)
        self.modify_bg(gtk.STATE_NORMAL, COLOR_WIDGET_BACKGROUND)

    def on_click(self, window, event):
        self.repaint()

    def expose(self, widget, event):
        print 'Widget::expose'
        cairo = widget.window.cairo_create()
        set_cairo_color(cairo, COLOR_WIDGET_FOREGROUND)
        cairo.rectangle(1, 1, self.grid_cols * GRID_LENGTH - 2, self.grid_rows * GRID_HEIGHT - 2)
        cairo.fill()

    def repaint(self):
        self.queue_draw()


class ValueDisplay(Widget):
    def __init__(self, param, grid_cols=1, grid_rows=1, value=0.0):
        Widget.__init__(self, grid_cols, grid_rows)
        self.param = param
        self.value = None
        self.set_value(value)

    def on_click(self, window, event):
        self.value = str(float(self.value) + 1.0)
        self.repaint()

    def set_value(self, value):
        self.value = str(value)

    def expose(self, widget, event):
        cairo = widget.window.cairo_create()
        set_cairo_color(cairo, COLOR_WIDGET_FOREGROUND)
        cairo.rectangle(1, 1, self.grid_cols * GRID_LENGTH - 2, self.grid_rows * GRID_HEIGHT - 2)
        cairo.fill()

        set_cairo_color(cairo, COLOR_WIDGET_TITLE)
        cairo.select_font_face("Helvetica")
        cairo.set_font_size(12)
        cairo.move_to(5, 15)
        cairo.show_text(self.param)

        set_cairo_color(cairo, COLOR_WIDGET_VALUE)
        cairo.select_font_face("Helvetica")
        cairo.set_font_size(18)
        cairo.move_to(5, self.grid_rows * GRID_HEIGHT * 0.80)
        cairo.show_text(self.value)

    def repaint(self):
        self.queue_draw()


class OnOffButton(Widget):
    def __init__(self, param, grid_cols=1, grid_rows=1):
        Widget.__init__(self, grid_cols, grid_rows)
        self.param = param
        self.is_on = False

    def set_on(self):
        self.is_on = True

    def set_off(self):
        self.is_on = False

    def toggle(self):
        self.is_on = not self.is_on

    def on_click(self, window, event):
        self.toggle()
        self.repaint()

    def expose(self, widget, event):
        w = self.allocation.width - 4
        h = self.allocation.height - 4
        cairo = widget.window.cairo_create()

        set_cairo_color(cairo, COLOR_WIDGET_FOREGROUND)
        cairo.rectangle(1, 1, self.grid_cols * GRID_LENGTH - 2, self.grid_rows * GRID_HEIGHT - 2)
        cairo.fill()

        set_cairo_color(cairo, COLOR_WIDGET_TITLE)
        cairo.select_font_face("Helvetica")
        cairo.set_font_size(12)
        cairo.move_to(5, 15)
        cairo.show_text(self.param)

        cairo.translate(2 + w * 0.1, 2 + h * 0.4)
        set_cairo_color(cairo, COLOR_WIDGET_TOGGLE)
        cairo.rectangle(0, 0, w * 0.8, h * 0.4)
        cairo.fill()

        if not self.is_on:
            cairo.translate(0, 0)
            set_cairo_color(cairo, COLOR_WIDGET_OFF)
            cairo.rectangle(0, 0, w * 0.4, h * 0.4)
            cairo.fill()
        else:
            cairo.translate(w * 0.4, 0)
            set_cairo_color(cairo, COLOR_WIDGET_ON)
            cairo.rectangle(0, 0, w * 0.4, h * 0.4)
            cairo.fill()

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
        v.set_value(123.45)

        v = ValueDisplay('HOTDOGS')
        self.fixed.put(v, GRID_LENGTH * 3, GRID_HEIGHT * 0)
        v.set_value(33.455)

        v = ValueDisplay('IS THERE A PROBLEM?', 4, 1)
        self.fixed.put(v, GRID_LENGTH * 0, GRID_HEIGHT * 1)
        v.set_value('YES THERE IS A PROBLEM')

        b = OnOffButton('Hello', 1, 1)
        self.fixed.put(b, GRID_LENGTH * 0, GRID_HEIGHT * 2)

        self.set_resizable(False)
        self.show_all()


Display()
gtk.main()