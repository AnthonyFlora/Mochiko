#!/usr/bin/env python

import Config
import paho.mqtt.client as mqtt
import gi
import datetime
import time
import Wynk
from threading import Thread
from collections import defaultdict

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
        if self.display is not None:
            self.display.set_image_from_jpeg(msg.payload)

    def run(self):
        print('MqttAdapter loop..')
        self.client.loop_forever()
        print('MqttAdapter loop done..')

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    # Setup
    image = Wynk.Wynk.Image()
    window = Wynk.Wynk(320, 240)
    window.add_widget(image, 0, 0)
    mqtt_adapter = MqttAdapter()
    mqtt_adapter.set_display(image)
    # Run
    mqtt_adapter.start()
    window.start()
    # Cleanup
    mqtt_adapter.client.disconnect()
    mqtt_adapter.join()