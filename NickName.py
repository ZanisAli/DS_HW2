from Tkinter import *
import re

class NickName(Toplevel):

    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        self.string = ''
        self.frame = Frame(self.top)
        self.top.title("Nickname")
        self.frame.pack()
        self.input()
        self.center()

    def input(self):
        r = self.frame

        k = Label(r,text="Your name :")
        k.pack(side='top')
        self.e = Entry(r,text='Name')
        self.e.pack()
        self.e.focus_set()
        b = Button(r,text='OK',command=self.gettext)
        b.pack(side='bottom')

    def gettext(self):
        self.string = self.e.get()
        if len(re.findall(r"[^\da-zA-Z]", self.string)) == 0 and len (self.string) > 0 and len (self.string) <= 8:
            self.top.destroy()


    def center(self):
        self.top.update_idletasks()
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        size = tuple(int(_) for _ in self.top.geometry().split('+')[0].split('x'))

if __name__ == '__main__':
        root = Tk()
        d = NickName(root)

        root.wait_window(d.top)
        name = d.getString()

        print name