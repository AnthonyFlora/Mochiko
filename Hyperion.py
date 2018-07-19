from collections import defaultdict
from datetime import datetime
from Queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from subprocess import Popen, PIPE, STDOUT
from sys import stdout
from threading import Thread
from time import sleep
from Tkinter import *
from ttk import Treeview
import shlex

# -- State -------------------------------------------------------------------------------------------------------------

subscriptions = defaultdict(lambda: [])
messages = Queue()
gui_callbacks = Queue()

# -- Functions ---------------------------------------------------------------------------------------------------------


def log(text):
    stdout.write('%s - %s\n' % (datetime.now(), text))
    stdout.flush()


def subscribe(topic, subscriber):
    global subscriptions
    subscriptions[topic].append(subscriber)


def unsubscribe(topic, subscriber):
    global subscriptions
    subscriptions[topic].remove(subscriber)


def publish(topic, message):
    global messages
    global subscriptions
    subscribers = subscriptions[topic]
    for subscriber in subscribers:
        subscriber.enqueue(topic, message)


def shutdown():
    log('Shutting down...')
    publish('shutdown', None)
    sleep(5)
    publish('shutdown_logger', None)

# -- Interfaces --------------------------------------------------------------------------------------------------------


class Processor(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.handlers = defaultdict(lambda: None)
        self.messages = Queue()
        self.running = False
        self.set_handler('shutdown', self.on_message_shutdown)

    def on_startup(self):
        self.log('Starting up')

    def on_shutdown(self):
        self.log('Shutting down')

    def enqueue(self, topic, message):
        self.messages.put((topic, message))

    def set_handler(self, topic, handler):
        self.handlers[topic] = handler
        subscribe(topic, self)
        self.log('Subcribed for %s' % topic)

    def on_message_shutdown(self, topic, message):
        self.running = False

    def run(self):
        self.on_startup()
        self.running = True
        while self.running:
            topic, message = self.messages.get()
            handler = self.handlers[topic]
            if handler:
                handler(topic, message)
            else:
                self.log('Unhandled topic %s' % topic)
        self.on_shutdown()

    def log(self, text):
        publish('log', '%s - %s' % (self.name, text))


class Logger(Processor):
    def __init__(self):
        Processor.__init__(self, 'Logger')
        self.set_handler('log', self.on_message_log)
        self.set_handler('shutdown_logger', self.on_message_shutdown_logger)

    def on_message_log(self, topic, message):
        log(message)

    def log(self, text):
        log('*** %s - %s' % (self.name, text))

    def on_message_shutdown(self, topic, message):
        None

    def on_message_shutdown_logger(self, topic, message):
        self.running = False


class Executor(Thread):
    def __init__(self, command, processor):
        Thread.__init__(self)
        self.command = command
        self.processor = processor
        self.process = Popen(shlex.split(self.command), stdin=PIPE, stderr=STDOUT, stdout=PIPE, close_fds=True)

    def run(self):
        self.processor.enqueue('executor_running', None)
        while True:
            line = self.process.stdout.readline()
            if line == '':
                self.processor.enqueue('executor_finished', None)
                break
            self.processor.enqueue('executor_data', line.strip())


    def send(self, data):
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def terminate(self):
        self.process.terminate()


class Application(Processor):
    def __init__(self, name, command):
        Processor.__init__(self, name)
        self.command = command
        self.set_handler('executor_running', self.on_message_executor_running)
        self.set_handler('executor_data', self.on_message_executor_data)
        self.set_handler('executor_finished', self.on_message_executor_finished)

    def on_startup(self):
        Processor.on_startup(self)
        self.log('Starting process: %s' % (self.command))
        self.start_executor()

    def start_executor(self):
        self.executor = Executor(self.command, self)
        self.executor.start()
        self.log('Started process: %s' % (self.command))

    def on_shutdown(self):
        Processor.on_shutdown(self)
        self.executor.terminate()

    def on_message_executor_running(self, topic, message):
        self.log('Application Running')

    def on_message_executor_data(self, topic, message):
        self.log('Application Data: %s' % (message))

    def on_message_executor_finished(self, topic, message):
        self.log('Application Finished: %s' % (message))


class SensorReceiver(Thread):
    def __init__(self, processor, connection):
        Thread.__init__(self)
        self.processor = processor
        self.connection = connection

    def run(self):
        self.processor.enqueue('receiver_running', None)
        try:
            while True:
                self.connection.send('w')
                data = self.connection.recv(1024)
                if data == '':
                    break
                self.processor.enqueue('receiver_data', data.strip())
                sleep(1)
        except:
            None
        self.processor.enqueue('receiver_finished', None)


class SensorController(Processor):
    def __init__(self, name, connection, address):
        Processor.__init__(self, name)
        self.connection = connection
        self.address = address
        self.set_handler('receiver_running', self.on_message_receiver_running)
        self.set_handler('receiver_data', self.on_message_receiver_data)
        self.set_handler('receiver_finished', self.on_message_receiver_finished)

    def on_startup(self):
        Processor.on_startup(self)
        log('startup')
        log(self.address)
        self.log('Starting receiver: %s:%s' % (self.address))
        self.receiver = SensorReceiver(self, self.connection)
        self.receiver.start()
        self.log('Started receiver: %s:%s' % (self.address))

    def on_shutdown(self):
        Processor.on_shutdown(self)
        self.connection.shutdown(SHUT_RDWR)
        self.connection.close()

    def on_message_receiver_running(self, topic, message):
        self.log('Receiver Running')

    def on_message_receiver_data(self, topic, message):
        self.log('Receiver Data: %s' % (message))
        m = re.match('\[ m=(.*) t=(.*) p=(.*) \]', message)
        if m:
            addr, port = self.address
            temp = float(m.group(2)) / 100.0
            pres = float(m.group(3)) / 100.0
            publish('sensor_weather_update', (addr, temp, pres))
            return

    def on_message_receiver_finished(self, topic, message):
        self.log('Receiver Finished: %s' % (message))


class TcpListener(Thread):
    def __init__(self, processor, port):
        Thread.__init__(self)
        self.processor = processor
        self.port = port
        self.server = None
        self.running = True

    def run(self):
        self.processor.enqueue('listener_running', None)
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.port))
        self.server.listen(10)
        try:
            while self.running:
                conn, addr = self.server.accept()
                self.processor.enqueue('tcp_connection', (conn, addr))
        except:
            None

    def shutdown(self):
        self.running = False
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(('127.0.0.1', self.port))
        s.shutdown


class TcpServer(Processor):
    def __init__(self, name, port, tcp_handler):
        Processor.__init__(self, name)
        self.port = port
        self.tcp_handler = tcp_handler
        self.set_handler('tcp_connection', self.on_message_tcp_connection)

    def on_startup(self):
        Processor.on_startup(self)
        self.log('Starting listener: %s' % (self.port))
        self.listener = TcpListener(self, self.port)
        self.listener.start()
        self.log('Started listener: %s' % (self.port))

    def on_message_tcp_connection(self, topic, message):
        conn, addr = message
        SensorController('SensorController_%s:%s' % addr, conn, addr).start()

    def on_shutdown(self):
        Processor.on_shutdown(self)
        self.listener.shutdown()


class SensorSummaryUpdater(Processor):
    def __init__(self, sensor_summary):
        Processor.__init__(self, 'SensorSummaryUpdater')
        self.set_handler('sensor_weather_update', self.on_message_sensor_weather_update)
        self.sensor_summary = sensor_summary

    def on_message_sensor_weather_update(self, topic, message):
        sensor, temperature, pressure = message
        self.sensor_summary.update(sensor, temperature, pressure)


class GatewaySummaryUpdater(Application):
    def __init__(self, gateway_summary):
        Application.__init__(self, 'GatewaySummaryUpdater', 'ssh -o ServerAliveInterval=5 -tt root@192.168.11.1 \'iwlist scan; iwconfig;\'')
        self.gateway_summary = gateway_summary
        self.current_gateway = None
        self.current_essid = None
        self.current_signal_strength = None
        self.current_frequency = None
        self.access_point = None

    def on_message_executor_running(self, topic, message):
        self.log('Application Running')

    def on_message_executor_data(self, topic, message):
        self.log('Application Data: %s' % (message))
        m = re.match('.*Access Point: (.*)', message)
        if m:
            self.access_point = m.group(1)
            self.gateway_summary.set_connected(self.access_point)
            self.log('Setting AP connected %s' % self.access_point)
            return
        m = re.match('.*Address: (.*)', message)
        if m:
            self.current_gateway = m.group(1)
            return
        m = re.match('.*Frequency:(.*) GHz.*', message)
        if m:
            self.current_frequency = m.group(1)
            return
        m = re.match('.*Signal level=(.*) dBm', message)
        if m:
            self.current_signal_strength = m.group(1)
            return
        m = re.match('.*ESSID:\"(.*)\"', message)
        if m:
            self.current_essid = m.group(1)
            if self.current_essid == 'xfinitywifi':
                self.gateway_summary.update(self.current_gateway, self.current_frequency, self.current_signal_strength)
            return

    def on_message_executor_finished(self, topic, message):
        self.log('Application Finished: %s' % (message))
        self.start_executor()


class ButtonUpdater(Processor):
    def __init__(self, button, heatmap):
        Processor.__init__(self, 'ButtonUpdater')
        self.set_handler('log', self.on_message_log)
        self.button = button
        self.heatmap = heatmap

    def on_message_log(self, topic, message):
        self.button['text'] = message
        #new = Tk()
        #Heatmap(new, 20, 20).pack(fill=BOTH, expand=True)

# -- Displays ----------------------------------------------------------------------------------------------------------

class Scatter(Canvas):
    def __init__(self, parent):
        None


class Histogram(Canvas):
    def __init__(self, parent):
        None


class Heatmap(Canvas):
    def __init__(self, parent, rows, cols):
        Canvas.__init__(self, parent, width=400, height=400, highlightthickness=0, bd=0, borderwidth=0, background='blue')
        self.rows = rows
        self.cols = cols
        self.data = [[0 for x in range(cols)] for y in range(rows)]
        self.after(1000, self.update)

    def update(self):
        cell_width = (float(self.winfo_width())) / float(self.cols)
        cell_height = (float(self.winfo_height())) / float(self.rows)
        self.delete('all')
        self.rects = [[self.create_rectangle(round(x * cell_width), round(y * cell_height), round((x + 1) * cell_width), round((y + 1) * cell_height), fill='gray') for x in range(self.cols)] for y in range(self.rows)]
        self.after(1000, self.update)


class SensorSummary(Treeview):
    def __init__(self, parent):
        Treeview.__init__(self, parent, columns=('Temperature (F)', 'Pressure (inHG)', 'Last Update'))
        self.heading('#0', text='Sensor (IP)')
        self.heading('#1', text='Temperature (F)')
        self.heading('#2', text='Pressure (inHG)')
        self.heading('#3', text='Last Update')
        self.column('#0', stretch=YES)
        self.column('#1', stretch=YES)
        self.column('#2', stretch=YES)
        self.column('#3', stretch=YES)

    def update(self, sensor, temperature, pressure):
        rows = self.get_children()
        for row in rows:
            if self.item(row)['text'] == sensor:
                self.item(row, text=sensor, values=(temperature, pressure, datetime.now()))
                return
        self.insert('', 'end', text=sensor, values=(temperature, pressure, datetime.now()))


class GatewaySummary(Treeview):
    def __init__(self, parent):
        Treeview.__init__(self, parent, columns=('Frequency (GHz)', 'Signal (dBm)', 'Connected', 'Last Update'))
        self.heading('#0', text='Gateway (MAC)')
        self.heading('#1', text='Frequency (GHz)')
        self.heading('#2', text='Signal (dBm)')
        self.heading('#3', text='Connected')
        self.heading('#4', text='Last Update')
        self.column('#0', stretch=YES)
        self.column('#1', stretch=YES)
        self.column('#2', stretch=YES)
        self.column('#3', stretch=YES)
        self.column('#4', stretch=YES)


    def update(self, gateway, frequency, signal):
        rows = self.get_children()
        for row in rows:
            if self.item(row)['text'] == gateway:
                is_connected = self.item(row)['values'][2]
                self.item(row, text=gateway, values=(frequency, signal, is_connected, datetime.now()))
                return
        self.insert('', 'end', text=gateway, values=(frequency, signal, '', datetime.now()))

    def set_connected(self, gateway):
        rows = self.get_children()
        for row in rows:
            if self.item(row)['text'] == gateway:
                log('Found it!')
                self.set(row, 'Connected', 'Yes')
            else:
                self.set(row, 'Connected', 'No')

# -- Execution ---------------------------------------------------------------------------------------------------------


if __name__ == "__main__":



    #Application('ifconfig', 'ssh -tt root@192.168.11.1 ifconfig').start()

    master = Tk()

    #master.after_idle(lambda: )

    s = SensorSummary(master)
    s.pack(fill=BOTH, expand=True)

    class ZZ(Button):
        def __init__(self, parent, s):
            Button.__init__(self, parent, text="OK", command=self.callback)
            self.s = s
        def callback(self):
            publish('log', 'Clicked')
            self.s.update('moo','temp','press')

    b = ZZ(master, s)
    b.pack()

    gateway_summary = GatewaySummary(master)
    gateway_summary.pack(fill=BOTH, expand=True)

    GatewaySummaryUpdater(gateway_summary).start()

    Logger().start()
    TcpServer('SensorServer', 8888, None).start()
    SensorSummaryUpdater(s).start()

    mainloop()
    shutdown()




