from Tkinter import *
import random
import pika
import uuid
import json

from NickName import NickName
from SelectServerDialog import SelectServerDialog
from SelectSessionDialog import SelectSessionDialog

offset = 20
cell_size = 50
cells = 9

class Board(Frame):
    def __init__(self, parent):

        Frame.__init__(self, parent)
        self.parent = parent
        self.player_name= ""
        self.session = None

        self.row, self.col = -1, -1
        self.size = offset * 2 + cell_size * cells

        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self, width=self.size * 2, height=self.size)
        self.canvas.pack(fill=BOTH, side=TOP)

        self.draw_grid()
        self.score = {}

        self.canvas.bind("<Button-1>", self.event_click)
        self.canvas.bind("<Key>", self.event_key)

        self.get_name()
        self.get_server()
        if not self.host:
            self.parent.destroy()
            return



        if not self.session:
            self.session, numbers, self.score = self.remote_create_session(self.player_name)
        else:
            self.session, numbers, self.score = self.remote_connect_session(self.session, self.player_name)

        self.redraw(numbers)


    def on_response(self, ch, method, props, body):

        if self.corr_id == props.correlation_id:
            self.response = body

    def remote_get_sessions(self):

        return self.call({"func": "get_sessions", "parms" : () })

    def remote_connect_session(self, session, player):

        return self.call({"func": "connect_session", "parms" : (session,player) })

    def remote_create_session(self, player):

        return self.call({"func": "create_session", "parms" : (player) })

    def remote_turn(self, session, player, x, y, n):

        return self.call({"func": "turn", "parms" : (session, player, x, y, n) })


    def call(self, data):

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='sudoku',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body= json.dumps(data))
        while self.response is None:
            self.connection.process_data_events()
        return json.loads(self.response)["result"]


        d = NickName(self.parent)
        self.wait_window(d.top)
        self.player_name = d.getString()

    def get_server(self):

        d = SelectServerDialog(self.parent)
        self.wait_window(d.top)
        self.host = d.result

    def select_session(self):

        d = SelectSessionDialog(self.parent, self.sessions)
        self.wait_window(d.top)
        if not d.result is None:
            self.session = self.sessions[d.result]

    def draw_grid(self):
         for i in xrange(10):
            width = 3 if i % 3 == 0 else 1

            x0 = offset + i * cell_size
            y0 = offset
            x1 = offset + i * cell_size
            y1 = self.size - offset
            self.canvas.create_line(x0, y0, x1, y1, fill="gray", width=width )

            x0 = offset
            y0 = offset + i * cell_size
            x1 = self.size - offset
            y1 = offset + i * cell_size
            self.canvas.create_line(x0, y0, x1, y1, fill="gray", width=width )

    def select(self):

        self.canvas.delete("frame")
        if self.row >= 0 and self.col >= 0:
            x0 = offset + self.col * cell_size + 1
            y0 = offset + self.row * cell_size + 1
            x1 = offset + (self.col + 1) * cell_size - 1
            y1 = offset + (self.row + 1) * cell_size - 1
            self.canvas.create_rectangle( x0, y0, x1, y1, outline="orange", width=3, tags="frame")

    def event_click(self, event):

        x, y = event.x, event.y
        if offset < x < self.size - offset and offset < y < self.size - offset:
            self.canvas.focus_set()
            row, col = (y - offset) / cell_size, (x - offset) / cell_size
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        self.select()

    def event_key(self, event):

        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.session, numbers, self.score = \
                self.remote_turn(self.session, self.player_name, self.col, self.row, int(event.char))
            self.redraw(numbers)



if __name__ == '__main__':
        root = Tk()
        b = Board(root)
        root.mainloop()