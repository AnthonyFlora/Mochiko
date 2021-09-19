from core import Service
from collections import defaultdict
import threading
import json
import time
import io
import picamera


# -----------------------------------------------------------------------------

class SurveillanceService(Service.Service):

    def __init__(self, hostname):
        Service.Service.__init__(self)
        self.hostname = hostname
        self.topic_global_config = 'surveillance/config'
        self.topic_sensor_config = 'surveillance/%s/config' % self.hostname
        self.topic_sensor_status = 'surveillance/%s/status' % self.hostname
        self.topic_sensor_stream = 'surveillance/%s/stream' % self.hostname
        self.config = defaultdict(lambda: None)
        self.config['fps'] = .1
        self.config['res_x'] = 320
        self.config['res_y'] = 240
        self.is_reconfig_needed = False
        self.camera = picamera.PiCamera()
        self.camera.framerate = self.config['fps']
        self.camera.resolution = (self.config['res_x'], self.config['res_y'])

    def on_connect(self, client, userdata, flags, rc):
        self.log('Connected')
        self.client.subscribe(self.topic_global_config)
        self.client.subscribe(self.topic_sensor_config)
        self.client.message_callback_add(self.topic_global_config, self.on_config)
        self.client.message_callback_add(self.topic_sensor_config, self.on_config)

    def processing_loop(self):
        self.log('processing loop started..')
        while True:
            # Handle reconfig
            self.client.publish(self.topic_sensor_status, json.dumps(self.config))
            self.camera.framerate = self.config['fps']
            self.camera.resolution = (self.config['res_x'], self.config['res_y'])
            # Send sensor data
            stream = io.BytesIO()
            for foo in self.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                size = stream.tell()
                stream.seek(0)
                self.client.publish(self.topic_sensor_stream, stream.read())
                stream.seek(0)
                stream.truncate()
                self.log('frame sent.. %d' % size)
                if self.is_reconfig_needed:
                    self.is_reconfig_needed = False
                    break

    def on_config(self, client, userdata, message):
        self.log('on_config -- ' + message.topic + ' : ' + str(message.payload))
        try:
            config = json.loads(message.payload)
            for key, value in config.items():
                self.config[key] = value
        except:
            None
        for key, value in self.config.items():
            self.log('config[%s] = %s' % (key, value))
        self.is_reconfig_needed = True


# -- Main ---------------------------------------------------------------------

if __name__ == '__main__':
    s = SurveillanceService('moocow')
    s.run()
