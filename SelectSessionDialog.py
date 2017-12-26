import Tkinter
from Tkinter import *
import threading
from socket import *
import json
import time


class SelectSessionDialog(Toplevel):
    lock = threading.Lock()

    def __init__(self, parent, sessions):
        self.top = Toplevel(parent)
        self.top.title("Session")

        self.parent = parent
        self.servers = {}

        self.make_widgets()
        self.poll()
        self.result = None
        self.center()

        for s in sessions:
            self.L.insert(Tkinter.END, s)

    def make_widgets(self):

        self.L = Listbox(self.top)
        self.L.pack(side=TOP, fill=Y)

        F2 = Tkinter.Frame(self.top)
        self.lab = Tkinter.Label(F2)
        btn1 = Tkinter.Button(F2, text="Select", command=self.select)
        btn2 = Tkinter.Button(F2, text="New", command=self.new)

        self.lab.pack()
        btn1.pack(side=Tkinter.LEFT)
        btn2.pack(side=Tkinter.RIGHT)
        F2.pack(side=Tkinter.TOP)


    def select(self):
        cs = self.L.curselection()
        self.result = cs[0]
        self.top.destroy()

    def new(self):
        self.top.destroy()

    def center(self):
        self.top.update_idletasks()
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        size = tuple(int(_) for _ in self.top.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.top.geometry("%dx%d+%d+%d" % (size + (x, y)))
        self.top.lift()

if __name__ == '__main__':
        root = Tk()

        root.wait_window(d.top)
        name = d.result

        print name