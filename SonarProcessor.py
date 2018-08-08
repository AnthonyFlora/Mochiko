import collections
import math


SPEED_OF_SOUND = 343.0
SAMPLING_RATE = 343.0


class Signal:
    def __init__(self, samples, sample_rate, time_original):
        self.samples = samples
        self.sample_rate = sample_rate
        self.time_original = time_original
        self.time_shifted = time_original

    def shift(self, time_shift):
        self.time_shifted += time_shift
        cells = time_shift * self.signal.sample_rate
        full = int(math.floor(cells))
        part = cells - full
        for i in range(len(self.samples) - 2, 0, -1):
            take = part * self.samples[i]
            print part, self.samples[i], take
            self.samples[i] -= take
            self.samples[i + 1] += take
        if full > 0:
            self.samples.rotate(full)
            for i in range(full):
                print i
                self.samples[i] = 0


class Sensor:
    def __init__(self, name, x, y):
        self.name = name
        self.location_x = x
        self.location_y = y
        self.signal = Signal()

    def set_signal(self, signal):
        self.signal = signal

    def shift(self, time_of_update):
        self.signal.shift(time_of_update)


class SonarProcessor:
    def __init__(self, num_cells_x, num_cells_y):
        self.time_last_update = 0.0
        self.density_map = [[0 for x in range(num_cells_x)] for y in range(num_cells_y)]
        self.sensors = collections.defaultdict(lambda: Sensor())

    def shift(self, time_of_update):
        for sensor in self.sensors:
            sensor.shift(time_of_update)

    def get_density_map(self):
        return self.density_map

s1 = Signal()

p = SonarProcessor()
print 's = ', s.samples
s.samples = collections.deque([0, 0, 1, 1, 0])
print 's = ', s.samples
s.shift(0.7)
print s.samples