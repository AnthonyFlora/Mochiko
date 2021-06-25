#! /usr/bin/python

# ManagementService
#   --> ComponentStatus
#   --> RunningServices
#   --> AvailableServices
#   <-- StartService
#   <-- StopService

# CameraService
#   --> ImageRequest
#   <-- ImageData

# WeatherService
#   --> WeatherRequest
#   <-- WeatherData

# SonarServic
#   --> SonarRequest
#   <-- SonarData

import paho.mqtt.client as mqtt
import json

TOPIC_ServiceStatus = 'hyperion/ServiceStatus/%s/ManagementService'
TOPIC_ManagementService_StartService = 'hyperion/%s/ManagementService/StartService'
TOPIC_ManagementService_StopService = 'hyperion/%s/ManagementService/StopService'


class ManagementService:
    def __init__(self, component_name):
        self.TOPIC_ServiceStatus = TOPIC_ServiceStatus % component_name
        self.TOPIC_ManagementService_StartService = TOPIC_ManagementService_StartService % component_name
        self.TOPIC_ManagementService_StopService = TOPIC_ManagementService_StopService % component_name
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.will_set(self.TOPIC_ServiceStatus, '', 0, retain=True)
        self.handlers = {}

    def start(self):
        self.client.connect("iot.eclipse.org", 1883, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print('Connected with result code: ' + str(rc))
        self.setup_handlers()
        self.setup_subscriptions()
        self.send_service_status()

    def setup_handlers(self):
        self.handlers[self.TOPIC_ManagementService_StartService] = self.on_message_start_service
        self.handlers[self.TOPIC_ManagementService_StopService] = self.on_message_stop_service

    def setup_subscriptions(self):
        self.client.subscribe(self.TOPIC_ManagementService_StartService)
        self.client.subscribe(self.TOPIC_ManagementService_StopService)

    def send_service_status(self):
        self.client.publish(self.TOPIC_ServiceStatus, 'RUNNING', 0, retain=True)

    def on_message(self, client, userdata, msg):
        print('Received message: ' + msg.topic)
        self.handlers[msg.topic](msg)

    def on_message_start_service(self, msg):
        print('Start Service: ' + msg.payload)

    def on_message_stop_service(self, msg):
        print('Stop Service: ' + msg.payload)


if __name__ == "__main__":
    service = ManagementService('TEST_001')
    service.start()

