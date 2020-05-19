# -*- coding: utf-8 -*-
# pylint: disable-all
"""

"""

from tkinter import *
from tkinter.ttk import *


class Table(Frame):

    def __init__(self, parent, dades, headers):
        self.__headers = headers

        Frame.__init__(self, parent)
        self.CreateUI()
        self.LoadTable(dades)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def CreateUI(self):
        tv = Treeview(self)
        header_key = [h.lower().replace(" ", "") for h in self.__headers[1:]]

        tv['columns'] = header_key
        first_col = self.__headers[0]

        tv.heading("#0", text=first_col, anchor='w')
        tv.column("#0", anchor="w")

        for h_key, header in zip(header_key, self.__headers[1:]):
            tv.heading(h_key, text=header, anchor='w')
            tv.column(h_key, anchor='w')

        tv.grid(sticky=(N, S, W, E))

        self.treeview = tv
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)

    def LoadTable(self, dades):
        for row in dades:
            values = []
            for val in row[1:]:
                values.append(val)
            self.treeview.insert('', 'end', text=row[0], values=values)


def make_table(title: str, dades, headers):
    root = Tk()
    root.title(title)
    Table(root, dades, headers)
    root.mainloop()
