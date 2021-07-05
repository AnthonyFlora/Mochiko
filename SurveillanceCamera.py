import time
import Service
import picamera
import io
import numpy as np


# -----------------------------------------------------------------------------

motion_dtype = np.dtype([
    ('x', 'i1'),
    ('y', 'i1'),
    ('sad', 'u2'),
    ])


class MotionDetector(object):

    def __init__(self, camera_width, camera_height):
        self.cols = (camera_width + 15) // 16
        self.cols += 1 # there's always an extra column
        self.rows = (camera_height + 15) // 16
        self.time_of_last_motion = 0
        self.recent_motion_threshold = 5.0

    def write(self, s):
        # Load the motion data from the string to a numpy array
        data = np.frombuffer(s, dtype=motion_dtype)
        # Re-shape it and calculate the magnitude of each vector
        data = data.reshape((self.rows, self.cols))
        data = np.sqrt(
            np.square(data['x'].astype(np.float)) +
            np.square(data['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)
        if (data > 30).sum() > 1:
            print('Motion detected!')
            self.time_of_last_motion = time.time()

    def is_recent_motion(self):
        time_since_last_motion = time.time() - self.time_of_last_motion
        is_recent_motion = time_since_last_motion <= self.recent_motion_threshold
        return is_recent_motion


class FrameThrottler(object):

    def __init__(self):
        self.time_between_frames = None
        self.time_of_next_frame = 0
        self.next = None

    def set_next(self, next):
        self.next = next

    def write(self, buf):
        # Non-JPEG stops routing
        if not buf.startswith(b'\xff\xd8'):
            return
        # Invalid FPS stops routing
        if not self.time_between_frames:
            return
        # Frame too early stops processing
        time_now = time.time()
        if not self.time_of_next_frame <= time_now:
            return
        # Schedule next frame
        self.time_of_next_frame = time_now + self.time_between_frames
        # Hand off processing to next
        if self.next:
            self.next(buf)

    def set_time_between_frames(self, time_between_frames):
        self.time_between_frames = time_between_frames


class FrameRecorder(object):

    def __init__(self, base='./'):
        self.base = base
        self.next = next
        self.path = ''
        self.file = None
        self.enabled = False

    def set_next(self, next):
        self.next = next

    def write(self, buf):
        # Write if enabled
        if self.enabled:
            if not self.file:
                self.path = self.base + Service.timestamp() + '.mjpeg'
                self.file = io.open(self.base + Service.timestamp() + '.mjpeg', 'wb')
                self.log('Started recording to %s' % self.path)
            if self.file:
                self.file(buf)
        if not self.enabled:
            if self.file:
                self.log('Stopped recording to %s' % self.path)
                self.file.close()
                self.file = None
                self.path = ''
        # Hand off processing to next
        if self.next:
            self.next(buf)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class SurveillanceCamera(Service.Service):

    def __init__(self):
        Service.Service.__init__(self)
        self.camera = picamera.PiCamera(resolution=(1024, 768), framerate=30)
        self.motion_detector = MotionDetector(320, 240)
        self.frame_recorder = FrameRecorder()
        self.frame_throttler = FrameThrottler()
        self.frame_throttler.next = self.frame_recorder

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
        self.camera.start_recording(self.frame_throttler, format='mjpeg') # hi res
        self.camera.start_recording('/dev/null', format='h264', motion_output=self.motion_detector, splitter_port=2, resize=(320, 240))
        while True:
            time_beg_loop = time.time()
            self.motion_detector.num_frames = 0
            self.camera.wait_recording(1)
            self.log('is_recent_motion=%d' % self.motion_detector.is_recent_motion())
            if self.motion_detector.is_recent_motion():
                self.frame_recorder.enable()
            else:
                self.frame_recorder.disable()
            time_end_loop = time.time()
            time_dur_loop = time_end_loop - time_beg_loop
            self.log('Processed FPS: %0.2f' % (self.motion_detector.num_frames / time_dur_loop))

    def send_stream_frame(self, frame):
        self.log('send_stream_frame')

    def start_stream(self):
        self.frame_router.stream_function = self.send_stream_frame

    def stop_stream(self):
        self.frame_router.stream_function = None

    def start_record(self):
        path = '%d.mjpeg' % time.time()
        self.frame_router.record_file = io.open(path, 'wb')
        self.log('Started recording to %s' % path)

    def stop_record(self):
        self.frame_router.record_file.close()
        self.frame_router.record_file = None
        self.log('Stopped recording')


# -----------------------------------------------------------------------------


if __name__ == '__main__':
    service = SurveillanceCamera()
    service.run()
