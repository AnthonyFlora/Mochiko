import pygtk

pygtk.require('2.0')
import gtk


class PyApp(gtk.Window):
    def __init__(self):
        super(PyApp, self).__init__()
        self.set_title("TreeView with ListStore")
        self.set_size_request(300, 200)
        self.set_resizable(False)
        self.connect('destroy', gtk.main_quit)

        store = gtk.ListStore(str, str)
        store.append(["PyQt", "aa"])
        store.append(["Tkinter", "bb"])
        store.append(["WxPython", "cc"])
        store.append(["PyGTK", "dd"])
        store.append(["PySide", "ee"])

        treeView = gtk.TreeView()
        treeView.set_size_request(250, 150)
        treeView.set_model(store)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Python GUI Libraries", rendererText, text=0)
        treeView.append_column(column)
        column = gtk.TreeViewColumn("FLOR", rendererText, text=1)
        treeView.append_column(column)

        fixed = gtk.Fixed()
        fixed.put(treeView, 25, 15)

        lbl2 = gtk.Label("Your choice is:")
        fixed.put(lbl2, 25, 175)
        self.label = gtk.Label("")

        fixed.put(self.label, 125, 175)
        self.add(fixed)

        treeView.connect("row-activated", self.on_activated)
        self.connect("destroy", gtk.main_quit)
        self.show_all()

    def on_activated(self, widget, row, col):
        model = widget.get_model()
        text = model[row][0]
        self.label.set_text(text)


def main():
    gtk.main()
    return


if __name__ == "__main__":
    bcb = PyApp()
    main()