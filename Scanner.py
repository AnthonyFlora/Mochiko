#! /usr/bin/python

import collections
import re
import shlex
from subprocess import Popen, PIPE

class Beacon(object):
    def __init__(self):
        self.address = ""
        self.ssid = ""
        self.signalBest = -999
        self.signalWorst = 999
        self.signalCurr = -999
        self.encryption = ""

def updateBeacons(beacons):

    for address, beacon in beacons.iteritems():
        beacon.signalCurr = 0
    
    command = "sudo iwlist wlan1 scan"
    process = Popen(shlex.split(command), stdout=PIPE)
    [output, error] = process.communicate()
    exit_code = process.wait()
    
    for line in output.splitlines():
        m = re.search('Address: (.*)', line)
        if m != None:
            beacon = beacons[m.group(1)]
            beacon.address = m.group(1)
        m = re.search('level=(.*) dBm', line)
        if m != None:
            beacon.signalCurr = int(m.group(1))
            beacon.signalBest = max(beacon.signalCurr, beacon.signalBest)
            beacon.signalWorst = min(beacon.signalCurr, beacon.signalWorst)
        m = re.search('level=(.*)/', line)
        if m != None:
            beacon.signalCurr = int(m.group(1))
            beacon.signalBest = max(beacon.signalCurr, beacon.signalBest)
            beacon.signalWorst = min(beacon.signalCurr, beacon.signalWorst)
        m = re.search('ESSID:"(.*)"', line)
        if m != None:
            beacon.ssid = m.group(1)
        m = re.search('Encryption key:(.*)', line)
        if m != None:
            beacon.encryption = m.group(1)

def displayBeacons(beacons):
    print ""
    print "Found %d beacons.." % len(beacons)
    for address, beacon in beacons.iteritems():
        print "%17s %4s %4d %4d %4d %s" % (beacon.address, beacon.encryption, beacon.signalBest, beacon.signalWorst, beacon.signalCurr, beacon.ssid)

def displayOpenBeacons(beacons):
    print ""
    print "Found %d beacons.." % len(beacons)
    for address, beacon in beacons.iteritems():
        if (beacon.encryption == "off") or (beacon.ssid == "FLORA_WIFI"):
          print "%17s %4s %4d %4d %4d %s" % (beacon.address, beacon.encryption, beacon.signalBest, beacon.signalWorst, beacon.signalCurr, beacon.ssid)

beacons = collections.defaultdict(Beacon)
while True:
    updateBeacons(beacons)
    displayOpenBeacons(beacons)

