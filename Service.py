import paho.mqtt.client as mqtt
import time
import Config
import traceback


def timestamp():
    return time.strftime('%Y%m%d_%H%M%S', time.localtime())


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
            self.processing_loop()
        except KeyboardInterrupt:
            self.log('Keyboard Interrupt..')
        except:
            self.log('Faulted..')
            traceback.print_exc()
        finally:
            self.client.loop_stop()
            self.log('Shutting down..')

    def connect_to_broker(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(username=Config.MQTT_BROKER_USER, password=Config.MQTT_BROKER_PASS)
        self.client.connect(Config.MQTT_BROKER_ADDR, Config.MQTT_BROKER_PORT)
    
    
