import paho.mqtt.client as mqtt
import time
import Config


def timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def log(text):
    print(timestamp() + ' -- ' + text)


# -----------------------------------------------------------------------------

class Service:

    def __init__(self):
        None

    def log(self, text):
        log(self.__class__.__name__ + ' : ' + text)

    def run(self):
        try:
            self.log('Connecting..')
            self.connect_to_broker()
            self.log('Processing..')
            self.client.loop_start()
            #self.processing_loop()
        except:
            self.log('Faulted..')
            self.client.loop_stop()
        finally:
            self.log('Shutting down..')

    def connect_to_broker(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(username=Config.MQTT_BROKER_USER, password=Config.MQTT_BROKER_PASS)
        self.client.connect(Config.MQTT_BROKER_ADDR, Config.MQTT_BROKER_PORT)

    # def on_connect(self, client, userdata, flags, rc):
    #   self.log('Connected')
    #   self.client.subscribe('ttt/moocow')
    #   self.client.message_callback_add('ttt/moocow', self.print_message_1)
    #   self.client.message_callback_add('ttt/#', self.print_message_2)
    #   self.client.publish('ttt/moocow', 'test')
    #
    # def on_disconnect(self, client, userdata, rc):
    #   self.log('Disconnected')
    #
    # def processing_loop(self):
    #   time.sleep(5)

    # def print_message_1(self, client, userdata, message):
    #   self.log('print_message_1 -- ' + message.topic + ' : ' +  message.payload)
    #
    # def print_message_2(self, client, userdata, message):
    #   self.log('print_message_2 -- ' + message.topic + ' : ' +  message.payload)
