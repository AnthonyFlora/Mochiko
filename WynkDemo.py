import Wynk
import glib
import subprocess
import types


def process(fd, condition):
    global a
    if condition == glib.IO_IN:
        print 'reading'
        b = fd.readline()
        a.v.set_value(b)
        print 'read', b
        return True
    elif condition == glib.IO_ERR:
        print 'err'
        return False
    elif condition == glib.IO_HUP:
        print 'hup'
        return False
    else:
        return 'unknown'
        return False


def start_process(self):
    print 'starting'
    global p, w
    p = subprocess.Popen("ping www.google.com", shell=True, stdout=subprocess.PIPE)
    w = glib.io_add_watch(p.stdout, glib.IO_IN, process)
    a.v.set_value('started')


def stop_process(self):
    print 'stopping'
    global p, w
    p.terminate()
    glib.source_remove(w)
    a.v.set_value('stopped')

w = None
p = None
a = Wynk.Display()

b = Wynk.OnOffButton('Hello', 6, 1)
b.on_change_on = types.MethodType(start_process, b)
b.on_change_off = types.MethodType(stop_process, b)
a.add_widget(b, 0, 2)

v = Wynk.ValueDisplay('MOO COW?', 6, 1)
a.add_widget(v, 0, 7)

t = Wynk.Table(6, 2)
a.add_widget(t, 0, 4)

a.show()



Wynk.start()