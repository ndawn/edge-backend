import json

import pika


class AMQPClient:
    def __init__(self, queue):
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)

    def __del__(self):
        self.connection.close()


class Producer(AMQPClient):
    def send(self, message):
        if not isinstance(message, str):
            try:
                message = json.dumps(message)
            except TypeError:
                message = str(message)

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=message,
        )


class Consumer(AMQPClient):
    def get(self):
        message = self.channel.basic_get(self.queue)

        if message[2] is not None:
            self.channel.basic_ack(message[0].delivery_tag)

            try:
                if type(message[2]).__name__ == 'bytes':
                    msg = message[2].decode('utf-8')
                else:
                    msg = message[2]
                return json.loads(msg)
            except json.JSONDecodeError:
                return message[2]
        else:
            return None
