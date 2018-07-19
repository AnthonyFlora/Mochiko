import Tkinter as tk


class HyperionViewer(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.title('Hyperion')
        self.val = tk.Entry(self, width=8)
        self.val.pack(side='left')
        self.add = tk.Button(self, text='Add', width=8)
        self.add.pack(side='left')
        self.rem = tk.Button(self, text='Remove', width=8)
        self.rem.pack(side='left')

    def set_val(self, value):
        self.val.delete(0, 'end')
        self.val.insert('end', str(value))


