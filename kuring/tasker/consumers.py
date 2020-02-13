
from asgiref.sync import async_to_sync
from channels.generic import websocket
import json
import logging


_l = logging.getLogger(__name__)


class Tasker(websocket.AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):

        return super(Tasker, self).__init__(*args, **kwargs)

    async def connect(self):
        await self.channel_layer.group_add('kuring', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('kuring', self.channel_name)

    async def receive(self, text_data):
        message = json.loads(text_data)['message']
        type = message['type']

        if type == 'ping':
            await self.sendMessage({'type': 'pong'})

    async def sendMessage(self, message):
        await self.send(text_data=json.dumps({'message': message}))

    async def plot_data(self, event):
        await self.sendMessage(event)

    async def task_finished(self, event):
        await self.sendMessage(event)
