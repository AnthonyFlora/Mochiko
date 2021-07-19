import Service
import time

# -----------------------------------------------------------------------------

class TestService(Service.Service):

    def __init__(self):
        Service.Service.__init__(self)

    def on_connect(self, client, userdata, flags, rc):
      self.log('Connected')
      self.client.subscribe('ttt/moocow')
      self.client.message_callback_add('ttt/moocow', self.print_message_1)
      self.client.message_callback_add('ttt/#', self.print_message_2)
      self.client.publish('ttt/moocow', 'test')
    
    def processing_loop(self):
      time.sleep(5)

    def print_message_1(self, client, userdata, message):
      self.log('print_message_1 -- ' + message.topic + ' : ' +  str(message.payload))
    
    def print_message_2(self, client, userdata, message):
      self.log('print_message_2 -- ' + message.topic + ' : ' +  str(message.payload))

# -- Main ---------------------------------------------------------------------

if __name__ == '__main__':
    s = TestService()
    s.run()