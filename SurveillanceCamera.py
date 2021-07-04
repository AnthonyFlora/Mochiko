import time
import Service
import picamera
import io


# -----------------------------------------------------------------------------

class SurveillanceCamera(Service.Service):

    def __init__(self):
        Service.Service.__init__(self)
        self.time_next_snapshot = 0.0
        self.time_between_snapshots = 1.0
        self.frame_num = 0
        self.output = None

    def on_connect(self, client, userdata, flags, rc):
      self.log('on_connect.. (rc=%d)' % rc)
      #self.client.subscribe('mochiko/surveillance/surveillance_start')
      #self.client.subscribe('mochiko/surveillance/surveillance_stop')
      #self.client.message_callback_add('mochiko/surveillance/surveillance_start', self.on_observation_start)
      #self.client.message_callback_add('mochiko/surveillance/surveillance_stop', self.on_observation_stop)

    def on_disconnect(self, client, userdata, rc):
        self.log('on_disconnect..')

    def processing_loop(self):
        self.log('processing_loop..')
        time.sleep(5)
        with picamera.PiCamera(resolution='720p', framerate=30) as camera:
            camera.start_preview()
        #     # Give the camera some warm-up time
        #     time.sleep(2)
        #     start = time.time()
        #     camera.start_recording(self, format='mjpeg')
        #     camera.wait_recording(5)
        #     camera.stop_recording()
        #     finish = time.time()

    def on_observation_start(self, client, userdata, message):
        self.log('on_observation_start -- ' + message.topic + ' : ' + str(message.payload))

    def on_observation_stop(self, client, userdata, message):
        self.log('on_observation_stop -- ' + message.topic + ' : ' + str(message.payload))

    def write(self, buf):
        print('write len %d' % len(buf))
        # if buf.startswith(b'\xff\xd8'):
        #     print('start new file')
        #     # Start of new frame; close the old one (if any) and
        #     # open a new output
        #     if self.output:
        #         self.output.close()
        #     self.frame_num += 1
        #     self.output = io.open('image.mjepg', 'ab')
        # self.output.write(buf)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    service = SurveillanceCamera()
    service.run()
