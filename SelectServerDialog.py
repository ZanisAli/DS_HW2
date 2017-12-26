import Tkinter
from Tkinter import *
import threading
from socket import *
import json
import time


class SelectServerDialog(Toplevel):
    lock = threading.Lock()

    def __init__(self, parent):
        self.top = Toplevel(parent)
        self.top.title("Server")

        self.parent = parent
        self.servers = {}

        self.make_widgets()
        self.poll()
        self.result = None
        self.center()

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', 12345))
        self.socket.settimeout(0.1)

    def make_widgets(self):

        self.L = Listbox(self.top)
        self.L.pack(side=TOP, fill=Y)

        F2 = Tkinter.Frame(self.top)
        self.lab = Tkinter.Label(F2)
        btn1 = Tkinter.Button(F2, text="Connect", command=self.connect)
        btn2 = Tkinter.Button(F2, text="Cancel", command=self.cancel)

        self.lab.pack()
        btn1.pack(side=Tkinter.LEFT)
        btn2.pack(side=Tkinter.RIGHT)
        F2.pack(side=Tkinter.TOP)

    def poll(self):

        try:
            m = self.socket.recvfrom(1024)
            ip = json.loads(m[0])["server_ip"]

            new = ip not in self.servers
            self.servers[ip] = time.time()
            if new:
                self.update_list()

            sel = self.L.curselection()
            self.lab.config(text=str(sel))

            if len(self.servers) >0 and time.time() - 100 > min(self.servers.values()):
                self.update_list()

        except:
            pass

        self.parent.after(200, self.poll)

    def update_list(self):
        self.servers = {i: t for i, t in self.servers.iteritems() if time.time() - t < 100}
        self.L.delete(0, END)
        for i in  sorted(self.servers.keys()):
            self.L.insert(Tkinter.END, i)

    def connect(self):
        cs = self.L.curselection()
        if len (cs) > 0:
            self.result= sorted(self.servers.keys())[cs[0]]
        self.top.destroy()

    def cancel(self):
        self.top.destroy()



if __name__ == '__main__':
        root = Tk()
        d = SelectServerDialog(root)

        root.wait_window(d.top)
        name = d.result

        print name