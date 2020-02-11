from channels.generic.websocket import WebsocketConsumer
import json


class Tasker(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        message = json.loads(text_data)['message']
        type = message['type']

        if type == 'ping':
            self.send(text_data=json.dumps({'type': 'pong'}))
