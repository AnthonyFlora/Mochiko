import collections
import datetime
import signal
import queue
import sys
import time
import paho.mqtt.client as mqtt
import tkinter as tk
from io import BytesIO
from PIL import ImageTk, Image, ImageFont, ImageDraw
import Config

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

  def update(self, img):
    self.img = img

    font = ImageFont.load_default() #ImageFont.truetype('Arial.ttf', 16)
    draw = ImageDraw.Draw(self.img)
    draw.text((0, 0), self.timestamp(), (255, 255, 255), font=font)

    self.img_tk = ImageTk.PhotoImage(self.img)
    self.canvas.itemconfig(self.img_canvas, image=self.img_tk)
    print('gui updated')

  def timestamp(self):
    return str(datetime.datetime.fromtimestamp(time.time()))

  def shutdown(self, event=None):
    self.quit()
    self.update()

  def on_sigint(self, sig, frame):
    self.shutdown()


# -----------------------------------------------------------------------------

class Control:

  def __init__(self, view):
    self.view = view

  def connect_to_broker(self):
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.on_disconnect = self.on_disconnect
    self.client.username_pw_set(username=Config.MQTT_BROKER_USER, password=Config.MQTT_BROKER_PASS)
    self.client.connect(Config.MQTT_BROKER_ADDR, Config.MQTT_BROKER_PORT)

  def setup_subscriptions(self):
    self.client.subscribe('surveillance/moocow/stream')
    self.client.message_callback_add('surveillance/moocow/stream', self.on_stream)

  def on_connect(self, client, userdata, flags, rc):
    print('Control connected..')

  def on_disconnect(self, client, userdata, rc):
    print('Control disconnected..')

  def on_stream(self, client, userdata, msg):
    print('Control received stream framei @ %s' % msg.topic)
    #stream = BytesIO(msg.payload)
    #img = Image.open(stream)
    #self.view.update(img)

  def on_message(self, client, userdata, msg):
    None

  def start(self):
    self.connect_to_broker()
    self.setup_subscriptions()
    self.client.loop_start()

  def stop(self):
    self.client.loop_stop()


# -----------------------------------------------------------------------------

view = View()
control = Control(view)

signal.signal(signal.SIGINT, view.on_sigint)

control.start()
view.mainloop()


