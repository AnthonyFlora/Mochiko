import collections
import datetime
import signal
import queue
import sys
import time
import tkinter as tk
from io import BytesIO
from PIL import ImageTk, Image, ImageFont, ImageDraw


# -----------------------------------------------------------------------------

class View(tk.Tk):

  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.bind('<Control-c>', self.shutdown)
    self.canvas = tk.Canvas(width=640, height=480)
    self.canvas.pack() 
    self.img = Image.new('RGB', (640, 480), (0, 0, 0))
    #self.img = Image.open('test.jpeg')
    self.img_tk = ImageTk.PhotoImage(self.img)
    self.img_canvas = self.canvas.create_image(20, 20, anchor=tk.NW, image=self.img_tk)
    self.update()

  def update(self):
    self.img = Image.open('test.jpeg')

    font = ImageFont.truetype('Arial.ttf', 16)
    draw = ImageDraw.Draw(self.img)
    draw.text((0, 0), self.timestamp(), (255, 255, 255), font=font)

    self.img_tk = ImageTk.PhotoImage(self.img)
    self.canvas.itemconfig(self.img_canvas, image=self.img_tk)
    self.after(1, self.update)

  def timestamp(self):
    return str(datetime.datetime.fromtimestamp(time.time()))

  def shutdown(self, event=None):
    self.quit()
    self.update()

  def on_sigint(self, sig, frame):
    self.shutdown()


# -----------------------------------------------------------------------------

class Control:

  def __init__(self):
    None

  def on_connect(self):
    None

  def on_disconnect(self):
    None

  def on_message(self):
    None

  def start(self):
    None

  def stop(self):
    None


# -----------------------------------------------------------------------------

view = View()
control = Control()

signal.signal(signal.SIGINT, view.on_sigint)

control.start()
view.mainloop()


