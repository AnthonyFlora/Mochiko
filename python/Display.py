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
    self.img_tk = ImageTk.PhotoImage(self.img)
    self.img_canvas = self.canvas.create_image(20, 20, anchor=tk.NW, image=self.img_tk)
    self.img_queue = queue.Queue()
    self.update_image()

  def queue_image(self, img):
    # Draw overlay
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), self.timestamp(), (255, 255, 255), font=font)
    # Change type, queue
    img_tk = ImageTk.PhotoImage(img)
    self.img_queue.put(img_tk)

  def update_image(self):
    if not self.img_queue.empty():
      self.img_tk = self.img_queue.get()
      self.canvas.itemconfig(self.img_canvas, image=self.img_tk)
      self.update()
      self.update_idletasks()
    self.after(10, self.update_image)

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
    self.stream = BytesIO()

  def connect_to_broker(self):
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.on_disconnect = self.on_disconnect
    self.client.username_pw_set(username=Config.MQTT_BROKER_USER, password=Config.MQTT_BROKER_PASS)
    self.client.connect(Config.MQTT_BROKER_ADDR, Config.MQTT_BROKER_PORT)
    self.time_last_message = time.time()

  def setup_subscriptions(self):
    self.client.subscribe('surveillance/moocow/stream')
    self.client.message_callback_add('surveillance/moocow/stream', self.on_stream)

  def on_connect(self, client, userdata, flags, rc):
    print('Control connected..')

  def on_disconnect(self, client, userdata, rc):
    print('Control disconnected..')

  def on_stream(self, client, userdata, msg):
    time_now = time.time()
    self.time_since_last_message = self.time_last_message - time_now
    self.time_last_message = time_now
    print('Control received stream frame @ %s, fps=%0.2f' % (msg.topic, 1.0 / self.time_since_last_message))
    self.stream.write(msg.payload)
    img = Image.open(self.stream)
    self.view.queue_image(img)
    self.stream.seek(0)
    self.stream.truncate()

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


