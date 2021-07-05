import time
import Service
import picamera
import io


# -----------------------------------------------------------------------------

class SurveillanceCamera(Service.Service):

    def __init__(self):
        Service.Service.__init__(self)
        self.time_next_snapshot = None
        self.time_between_snapshots = 1.0
        self.frame_num = 0
        self.output = None

    def on_connect(self, client, userdata, flags, rc):
      self.log('on_connect.. (rc=%d)' % rc)
      self.client.subscribe('mochiko/surveillance/surveillance_start')
      self.client.subscribe('mochiko/surveillance/surveillance_stop')
      self.client.message_callback_add('mochiko/surveillance/surveillance_start', self.on_observation_start)
      self.client.message_callback_add('mochiko/surveillance/surveillance_stop', self.on_observation_stop)

    def on_disconnect(self, client, userdata, rc):
        self.log('on_disconnect..')

    def processing_loop(self):
        self.log('processing_loop..')
        with picamera.PiCamera(resolution='720p', framerate=30) as camera:
            camera.start_preview()
            time.sleep(2) # Give the camera some warm-up time
            camera.start_recording(self, format='mjpeg')
            while True:
                camera.wait_recording(1)

    def on_observation_start(self, client, userdata, message):
        self.log('on_observation_start -- ' + message.topic + ' : ' + str(message.payload))

    def on_observation_stop(self, client, userdata, message):
        self.log('on_observation_stop -- ' + message.topic + ' : ' + str(message.payload))

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            if not self.time_next_snapshot:
                self.time_next_snapshot = time.time()
            if self.time_next_snapshot <= time.time():
                self.log('taking snapshot, write len %d' % len(buf))
                self.time_next_snapshot = self.time_next_snapshot + self.time_between_snapshots
                self.output = io.open('%d.jpg' % time.time(), 'wb')
                self.output.write(buf)
                self.output.close()

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    service = SurveillanceCamera()
    service.run()
