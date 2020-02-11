
from asgiref.sync import async_to_sync
from channels.generic import websocket
import json


class Tasker(websocket.WebsocketConsumer):

    chGroup = 'kuring'
    chName = 'tasker'

    def connect(self):

        async_to_sync(self.channel_layer.group_add)(self.chGroup, self.chName)
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        message = json.loads(text_data)['message']
        type = message['type']

        if type == 'ping':
            self.sendMessage({'type': 'pong'})

    def sendMessage(self, message):
        self.send(text_data=json.dumps({'message': message}))
