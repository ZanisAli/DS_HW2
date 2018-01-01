import Tkinter
from Tkinter import *
import threading
from socket import *
import json
import time


class SelectServerDialog(Toplevel):
    lock = threading.Lock()

    def __init__(self, parent):
        #Frame.__init__(self, parent)
        self.top = Toplevel(parent)
        self.top.title("Server")

        self.parent = parent
        self.servers = {}
        #self.top.pack()
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
            #print ip

            new = ip not in self.servers
            self.servers[ip] = time.time()
            if new:
                self.update_list()

  if time.time() - t < 100}
        self.L.delete(0, END)
        for i in  sorted(self.servers.keys()):
            self.L.insert(Tkinter.END, i)
if __name__ == '__main__':
        root = Tk()
        d = SelectServerDialog(root)

        root.wait_window(d.top)
        name = d.result

        print name