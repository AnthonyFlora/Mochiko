#!/usr/bin/python

import gobject
import gtk
import collections
import math


class ValueDisplay(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.connect('expose-event', self.expose)


class Window