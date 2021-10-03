#!/usr/bin/env python

import Config
import paho.mqtt.client as mqtt
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from threading import Thread

# -----------------------------------------------------------------------------


class Display(Gtk.Window):

    def __init__(self):
        super(Display, self).__init__()
        self.set_title('Display')
        self.set_size_request(320, 240)
        self.image = Gtk.Image()
        self.add(self.image)
        self.connect('destroy', Gtk.main_quit)
        self.show_all()

    def set_image(self, pixbuf):
        self.image.set_from_pixbuf(pixbuf)
        print('Image changed')

# -----------------------------------------------------------------------------


class MqttAdapter(Thread):

    def __init__(self):
        super(MqttAdapter, self).__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(username=Config.MQTT_BROKER_USER, password=Config.MQTT_BROKER_PASS)
        self.client.connect(Config.MQTT_BROKER_ADDR, Config.MQTT_BROKER_PORT)
        self.client.subscribe('surveillance/moocow/stream')
        self.client.message_callback_add('surveillance/moocow/stream', self.on_stream)
        self.display = None

    def set_display(self, display):
        self.display = display

    def on_connect(self, client, userdata, flags, rc):
        print('Control connected..')

    def on_disconnect(self, client, userdata, rc):
        print('Control disconnected..')

    def on_stream(self, client, userdata, msg):
        print('Control received stream frame @ %s' % msg.topic)
        if self.display is not None:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(msg.payload)
            loader.close()
            pixbuf = loader.get_pixbuf()
            self.display.set_image(pixbuf)

    def run(self):
        print('MqttAdapter loop..')
        self.client.loop_forever()
        print('MqttAdapter loop done..')

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    # Setup
    display = Display()
    mqtt_adapter = MqttAdapter()
    mqtt_adapter.set_display(display)
    # Run
    mqtt_adapter.start()
    Gtk.main()
    # Cleanup
    mqtt_adapter.client.disconnect()
    mqtt_adapter.join()