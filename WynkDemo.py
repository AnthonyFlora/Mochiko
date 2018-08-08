import Wynk
import glib
import subprocess
import types


def process(fd, condition):
    global a
    if condition == glib.IO_IN:
        b = fd.readline()
        a.v.set_value(b)
        return True
    else:
        return False


def start_process(self):
    print 'starting'
    global p, w
    p = subprocess.Popen("ping www.google.com", shell=True, stdout=subprocess.PIPE)
    w = glib.io_add_watch(p.stdout, glib.IO_IN, process)


def stop_process(self):
    print 'stopping'
    global p, w
    p.terminate()
    glib.source_remove(w)

w = None
p = None
a = Wynk.Display()

b = Wynk.OnOffButton('Hello', 1, 1)
b.on_change_on = types.MethodType(start_process, b)
b.on_change_off = types.MethodType(stop_process, b)
a.add_widget(b, 0, 2)

v = Wynk.ValueDisplay('MOO COW?', 8, 1)
a.add_widget(v, 0, 7)

t = Wynk.Table(6, 2)
a.add_widget(t, 0, 4)

a.show()



Wynk.start()