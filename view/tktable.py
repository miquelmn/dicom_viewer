from tkinter import *
from tkinter.ttk import *


class Table(Frame):

    def __init__(self, parent, dades):
        Frame.__init__(self, parent)
        self.CreateUI()
        self.LoadTable(dades)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def CreateUI(self):
        tv = Treeview(self)
        tv['columns'] = ('starttime')
        tv.heading("#0", text='Sources', anchor='w')
        tv.column("#0", anchor="center")
        tv.heading('starttime', text='Start Time')
        tv.column('starttime', anchor='center')
        tv.grid(sticky=(N, S, W, E))

        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)

    def LoadTable(self, dades):
        for row in dades:
            self.treeview.insert('', 'end', text=row[0], values=(row[1],))


def make_table(title: str, dades):
    root = Tk(title)
    Table(root, dades)
    root.mainloop()
