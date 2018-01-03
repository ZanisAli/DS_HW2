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
        """
        Sudoku board implementation
        :param parent: Tk parent object
        """
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
        # look for broadcasting servers and select one
        self.get_server()
        if not self.host:
            self.parent.destroy()
            return

        # connect to RabbirMQ
        self.connect()
        # get sesiions list
        self.sessions = self.remote_get_sessions()
        # and select one
        self.select_session()

        if not self.session:
            self.session, numbers, self.score = self.remote_create_session(self.player_name)
        else:
            self.session, numbers, self.score = self.remote_connect_session(self.session, self.player_name)

        self.redraw(numbers)

    def connect(self):
        """
        Connecting to RabbitMQ queue on remote host
        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()

        # declaring callback queue an listening to it
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        """
        callback function for server responses
        :param ch: not used
        :param method: not used
        :param props: not used
        :param body: json string with server answer
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def remote_get_sessions(self):
        """
        get sessions list from server
        :return: server answer
        """
        return self.call({"func": "get_sessions", "parms" : () })

    def remote_connect_session(self, session, player):
        """

        :param session:
        :param player:
        :return:
        """
        return self.call({"func": "connect_session", "parms" : (session,player) })

    def remote_create_session(self, player):
        """
        creates new session on server
        :param player: nickname
        :return: game status
        """
        return self.call({"func": "create_session", "parms" : (player) })

    def remote_turn(self, session, player, x, y, n):
        """
        Make turn
        :param session: name
        :param player: name
        :param x: row
        :param y: column
        :param n: number to put on board
        :return: game status
        """
        return self.call({"func": "turn", "parms" : (session, player, x, y, n) })


    def call(self, data):
        """
        convert parameters to json string
        sent to server
        wain for answer
        and convert answer to dict
        :param data: parameters
        :return: dict with parameters
        """
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


    def get_name(self):
        """
        show dialog for nickname
        """
        d = NickName(self.parent)
        self.wait_window(d.top)
        self.player_name = d.getString()

    def get_server(self):
        """
        shaow dialog for server select
        """
        d = SelectServerDialog(self.parent)
        self.wait_window(d.top)
        self.host = d.result

    def select_session(self):
        """
        show dialog for session select
        """
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
        """
        select cell on board
        """
        self.canvas.delete("frame")
        if self.row >= 0 and self.col >= 0:
            x0 = offset + self.col * cell_size + 1
            y0 = offset + self.row * cell_size + 1
            x1 = offset + (self.col + 1) * cell_size - 1
            y1 = offset + (self.row + 1) * cell_size - 1
            self.canvas.create_rectangle( x0, y0, x1, y1, outline="orange", width=3, tags="frame")

    def event_click(self, event):
        """
        mouse click event processing
        :param event:
        """
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
        """
        key press processing
        :param event:
        """
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.session, numbers, self.score = \
                self.remote_turn(self.session, self.player_name, self.col, self.row, int(event.char))
            self.redraw(numbers)

    def redraw (self, numbers):
        """
        redraw sodocu board
        :param numbers: array of numbers, if zero left cell blank
        """
        self.canvas.delete("score")
        self.canvas.create_text(self.size+20, offset, text="Score", tags="score", anchor='w', fill="black")

        s = sorted(self.score.items(), key=lambda x: -x[1])

        for n, (name, score) in enumerate(s):
            text = "{}: {}".format(name, score)
            color = "blue" if name == self.player_name else "black"
            self.canvas.create_text(self.size + 20, offset + (n +1) * 20, text=text, tags="score", anchor='w', fill=color)

        self.canvas.delete("numbers")

        numbers = list(numbers)

        for i in xrange(cells):
            for j in xrange(cells):
                x = offset + i * cell_size + cell_size / 2
                y = offset + j * cell_size + cell_size / 2

                text = numbers.pop(0)
                if text >0:
                    self.canvas.create_text(x, y, text=text, tags="numbers", fill="black")

if __name__ == '__main__':
        root = Tk()
        b = Board(root)
        root.mainloop()