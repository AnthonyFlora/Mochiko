#! /usr/bin/python

# Wynk
#
#

# -- Imports ------------------------------------------------------------------

import cairo
import datetime
import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk


# -- Core ---------------------------------------------------------------------

class Wynk(Gtk.Window):

    def __init__(self, width=320, height=240):
        # Window
        super(Wynk, self).__init__()
        self.set_title('Display')
        self.set_size_request(width, height)
        self.set_resizable(False)
        self.layout = Gtk.Fixed()
        self.add(self.layout)
        # Signals
        self.connect('destroy', Gtk.main_quit)

    def add_widget(self, widget, x, y):
        self.layout.put(widget, x, y)

    def start(self):
        self.show_all()
        Gtk.main()

    class Image(Gtk.DrawingArea):

        def __init__(self, name='Image', image_width=320, image_height=240, requested_fps=None):
            # Container
            super(Wynk.Image, self).__init__()
            self.name = name
            self.image_width = image_width
            self.image_height = image_height
            self.scaled_pixbuf = None
            self.requested_fps = requested_fps
            self.set_size_request(self.image_width, self.image_height)
            self.connect('draw', self._on_draw)
            self.time_last_draw = time.time()
            self.actual_fps = 0
            self.estimated_draw_time = 0
            self._schedule_next_tick()

        def set_image_from_pixbuf(self, pixbuf):
            is_width_match = (pixbuf.get_width() == self.image_width)
            is_height_match = (pixbuf.get_height() == self.image_height)
            is_dimension_match = is_width_match and is_height_match
            self.scaled_pixbuf = pixbuf
            if not is_dimension_match:
                print(self.name, ' scaling (%d %d) to (%d %d)' % (pixbuf.get_width(), pixbuf.get_height(), self.image_width, self.image_height))
                self.scaled_pixbuf = pixbuf.scale_simple(self.image_width, self.image_height, GdkPixbuf.InterpType.BILINEAR)
            self._tick()

        def set_image_from_jpeg(self, jpeg):
            loader = GdkPixbuf.PixbufLoader()
            loader.write(jpeg)
            loader.close()
            pixbuf = loader.get_pixbuf()
            self.set_image_from_pixbuf(pixbuf)

        def _schedule_next_tick(self):
            print(self.name, ' tick')
            if self.requested_fps is not None:
                delay = round((1 / self.requested_fps - self.estimated_draw_time) * 1000)
                GLib.timeout_add(delay, self._tick)

        def _tick(self):
            self.queue_draw()
            self._schedule_next_tick()
            return False

        def _update_actual_fps(self):
            time_curr = time.time()
            time_diff = time_curr - self.time_last_draw
            self.time_last_draw = time.time()
            self.actual_fps = 1 / time_diff

        def _draw_background(self, cr):
            if self.scaled_pixbuf:
                Gdk.cairo_set_source_pixbuf(cr, self.scaled_pixbuf, 0, 0)
                cr.paint()
            else:
                cr.set_source_rgb(0, 0, 0)
                cr.rectangle(0, 0, self.image_width, self.image_height)
                cr.fill()

        def _draw_timestamp(self, cr):
            cr.set_source_rgb(255, 255, 0)
            cr.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(12)
            cr.move_to(0, 240)
            cr.show_text('%s (%0.3f FPS)' % (datetime.datetime.now(), self.actual_fps))
            cr.stroke()

        def _on_draw(self, area, cr):
            print(self.name, ' draw')
            time_draw_beg = time.time()
            self._update_actual_fps()
            self.render(cr)
            time_draw_end = time.time()
            self.estimated_draw_time = time_draw_end - time_draw_beg

        def render(self, cr):
            self._draw_background(cr)
            self._draw_timestamp(cr)


# -- Example ------------------------------------------------------------------

if __name__ == '__main__':

    pixbuf = GdkPixbuf.Pixbuf.new_from_file('test.jpeg')

    image1 = Wynk.Image(name='Image1', requested_fps=1)
    image1.set_image_from_pixbuf(pixbuf)
    image2 = Wynk.Image(name='Image2')
    image2.set_image_from_pixbuf(pixbuf)

    wynk = Wynk(320, 2*240)
    wynk.add_widget(image1, 0, 0)
    wynk.add_widget(image2, 0, 240)
    wynk.start()
