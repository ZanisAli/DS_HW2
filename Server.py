import threading
from socket import *
import time
import json
import pika
import random
import copy

cells = 9


class Session():
    def __init__(self):

        self.random_numbers()
        self.init_numbers = [n if random.random() > 0.7 else 0 for n in self.numbers]

        self.visible_numbers = {}
        self.scores = {}

    def random_numbers(self):

        test = list("217385469385469712496721835524816973639547281871293546762158394953674128148932657")
        self.numbers = [int(n) for n in test]

    def new_player(self, name):

        self.visible_numbers[name] = self.init_numbers[:]
        self.scores[name] = 0

    def turn(self, name, x, y, n):

        # type: (object, object, object, object) -> object
        self.scores[name] -=1
        if self.numbers[y + cells * x] == int(n):
            self.visible_numbers[name][y + cells * x] = int(n)
            self.scores[name] += 2
        return self.visible_numbers[name]


class SudokuServer():

    def __init__(self):

        self.get_ip_address()
        self.sessions = {}
        self.session_max = 0
        self.create_queue()
        thread = threading.Thread(target=self.broadcast, args=())
        thread.daemon = True
        thread.start()

    def create_queue(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='sudoku')

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue='sudoku')

    def on_request(self, ch, method, props, body):

        data = json.loads(body)
        # get function name anf call this function with given params
        result = getattr(self, data["func"])( data["parms"])

        response = {"result" : result}

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id= \
                                                             props.correlation_id),
                         body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)






    def broadcast(self):

        while True:
            s=socket(AF_INET, SOCK_DGRAM)
            s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            j = json.dumps({"server_ip" : self.ip})
            s.sendto(j,('255.255.255.255',12345))
            time.sleep(3)

    def get_ip_address(self):

        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip =  s.getsockname()[0]

if __name__ == '__main__':
        srv = SudokuServer()
        srv.channel.start_consuming()
