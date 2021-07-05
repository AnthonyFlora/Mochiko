import time
import Service
import picamera
import io


# -----------------------------------------------------------------------------

class MotionDetector(object):

    def __init__(self):
        self.time_of_last_motion = 0
        self.recent_motion_threshold = 1.0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            None # detect motion, store time

    def is_recent_motion(self):
        time_since_last_motion = time.time() - self.time_of_last_motion
        is_recent_motion = time_since_last_motion <= self.recent_motion_threshold
        return is_recent_motion

class FrameRouter(object):

    def __init__(self):
        self.time_between_frames = None
        self.time_of_next_frame = 0
        self.stream_function = None
        self.record_file = None

    def write(self, buf):
        # Invalid FPS stops routing
        if not self.time_between_frames:
            return

        # Non-JPEG stops routing
        if not buf.startswith(b'\xff\xd8'):
            return

        # Frame too early stops processing
        time_now = time.time()
        is_frame_expired = self.time_of_next_frame <= time_now
        if not is_frame_expired:
            return

        # If enabled, stream frame
        if self.stream_function:
            self.log('sending stream, len %d' % len(buf))
            self.stream_function(buf)

        # If enabled, record frame
        if self.record_file:
            self.record_file.write(buf)

        # Schedule next frame
        self.time_of_next_frame = time_now + self.time_between_frames

    def set_frames_per_second(self, fps):
        if fps == 0.0:
            self.time_between_frames = None
        else:
            self.time_between_frames = 1.0 / fps


class SurveillanceCamera(Service.Service):

    def __init__(self):
        Service.Service.__init__(self)
        self.motion_detector = MotionDetector()
        self.frame_router = FrameRouter()
        self.time_last_motion = 0

    def on_connect(self, client, userdata, flags, rc):
        self.log('on_connect.. (rc=%d)' % rc)
        # self.client.subscribe('mochiko/surveillance/surveillance_start')
        # self.client.subscribe('mochiko/surveillance/surveillance_stop')
        # self.client.message_callback_add('mochiko/surveillance/surveillance_start', self.on_observation_start)
        # self.client.message_callback_add('mochiko/surveillance/surveillance_stop', self.on_observation_stop)

    def on_disconnect(self, client, userdata, rc):
        self.log('on_disconnect..')

    def processing_loop(self):
        self.log('processing_loop..')
        with picamera.PiCamera(resolution=(1024, 768), framerate=30) as camera:
            camera.start_recording(self.frame_router, format='mjpeg') # hi res
            camera.start_recording(self.motion_detector, format='mjpeg', splitter_port=2, resize=(320, 240))
            self.frame_router.set_frames_per_second(30)
            self.start_record()
            while True:
                camera.wait_recording(1)
                if self.motion_detector.is_recent_motion():
                    None

    def send_stream_frame(self, frame):
        self.log('send_stream_frame')

    def start_stream(self):
        self.frame_router.stream_function = self.send_stream_frame

    def stop_stream(self):
        self.frame_router.stream_function = None

    def start_record(self):
        self.frame_router.record_file = io.open('%d.mjpeg' % time.time(), 'wb')

    def stop_record(self):
        self.frame_router.record_file.close()
        self.frame_router.record_file = None


# -----------------------------------------------------------------------------


if __name__ == '__main__':
    service = SurveillanceCamera()
    service.run()
