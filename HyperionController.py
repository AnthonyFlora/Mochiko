import HyperionModel
import HyperionViewer
import Tkinter as tk


def on_change(data):
    print data


def add():
    model.x.set(model.x.get() + 1)


def sub():
    model.x.set(model.x.get() - 1)


root = tk.Tk()
root.withdraw()

view = HyperionViewer.HyperionViewer(root)
model = HyperionModel.HyperionModel()

model.x.add_callback(on_change)
model.x.add_callback(view.set_val)
view.add.config(command=add)
view.rem.config(command=sub)

model.x.set(99)


tk.mainloop()