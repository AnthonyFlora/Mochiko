#! /usr/bin/python


class XYZ():
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0


class Target():
    def __init__(self):
        self.position = XYZ()
        self.velocity = XYZ()
        self.acceleration = XYZ()
        self.time_last_update = 0.0


class Element():
    def __init__(self):
        self.position = XYZ()

    def receive(self, duration):
        None


class Detector():
    def __init__(self):
        None


class Scheduler():
    def __init__(self):
        None


class Tracker():
    def __init__(self):
        None


class Simulator():
    def __init__(self):
        None

