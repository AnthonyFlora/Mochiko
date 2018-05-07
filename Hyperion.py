from collections import defaultdict
from datetime import datetime
from Queue import Queue
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE, STDOUT
from sys import stdout
from threading import Thread
from time import sleep
from Tkinter import *
import shlex


# -- State -------------------------------------------------------------------------------------------------------------

running = False
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
    global running
    global subscriptions
    subscribers = subscriptions[topic]
    for subscriber in subscribers:
        subscriber.enqueue(topic, message)


def stop():
    global running
    running = False

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

    def on_message_log(self, topic, message):
        log(message)

    def log(self, text):
        log('*** %s - %s' % (self.name, text))


class Executor(Thread):
    def __init__(self, command, processor):
        Thread.__init__(self)
        self.command = command
        self.processor = processor
        self.process = Popen(shlex.split(self.command), stdin=PIPE, stderr=STDOUT, stdout=PIPE)

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

class TcpStreamer(Thread):
    def __init__(self, processor, connection):
        Thread.__init__(self)
        self.processor = processor
        self.connection = connection

    def run(self):
        log('Streamer for connection %s started..' % (self.connection))
        self.processor.enqueue('streamer_running', None)
        while True:
            self.connection.send('w')
            data = self.connection.recv(1024)
            if data == '':
                break
            self.processor.enqueue('streamer_data', data.strip())
            sleep(5)

        self.processor.enqueue('streamer_finished', None)
        log('Streamer for connection %s finished..' % (self.connection))



class TcpListener(Thread):
    def __init__(self, processor, port):
        Thread.__init__(self)
        self.processor = processor
        self.port = port

    def run(self):
        self.processor.enqueue('listener_running', None)
        s = socket(AF_INET, SOCK_STREAM)
        s.bind(('0.0.0.0', self.port))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            self.processor.enqueue('tcp_connection', (conn, addr))



class TcpServer(Processor):
    def __init__(self, name, port, tcp_handler):
        Processor.__init__(self, name)
        self.port = port
        self.tcp_handler = tcp_handler
        self.set_handler('tcp_connection', self.on_message_tcp_connection)
        self.set_handler('streamer_data', self.on_message_streamer_data)

    def on_startup(self):
        Processor.on_startup(self)
        self.log('Starting listener: %s' % (self.port))
        self.listener = TcpListener(self, self.port)
        self.listener.start()
        self.log('Started listener: %s' % (self.port))

    def on_message_tcp_connection(self, topic, message):
        conn, addr = message
        TcpStreamer(self, conn).start()

    def on_message_streamer_data(self, topic, message):
        self.log('Streamer Data: %s' % (message))



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

    def log(self, text):
        log('%s - %s' % (self.name, text))

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


# -- Execution ---------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    Logger().start()
    Processor('p1').start()
    TcpServer('tcp', 8888, None).start()

    #Application('ifconfig', 'ssh -tt root@192.168.11.1 ifconfig').start()

    master = Tk()

    #master.after_idle(lambda: )

    class ZZ(Button):
        def __init__(self, parent):
            Button.__init__(self, parent, text="OK", command=self.callback)
        def callback(self):
            publish('log', 'Clicked')

    b = ZZ(master)
    b.pack()

    h = Heatmap(master, 20, 20)
    h.pack(fill=BOTH, expand=True)

    mainloop()
    publish('shutdown', None)
