
from asgiref.sync import async_to_sync
from channels.generic import websocket
import json
import logging

from tasker import models, tasks

_l = logging.getLogger(__name__)


class Tasker(websocket.AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add('kuring', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('kuring', self.channel_name)

    async def receive(self, text_data):
        # _l.info(f'> text_data = {text_data}')
        message = json.loads(text_data)['message']
        type = message['type']

        if type == 'ping':
            await self.sendMessage({'type': 'pong'})
            return
        if type == 'runTask':
            await models.taskLaunched(message['taskId'])
            return
        if type == 'stopTask':
            # await self.channel_layer.group_send('kuring', message)
            await models.taskStopped(message['taskId'])
            return
        if type == 'reportDelay':
            # await self.channel_layer.group_send('kuring', message)
            tasks.saveDelay.delay(message['taskId'], message['t'], message['d'], message['j'])
            return

    async def sendMessage(self, message):
        await self.send(text_data=json.dumps({'message': message}))

    async def plot_data(self, event):
        await self.sendMessage(event)

    async def task_finished(self, event):
        await self.sendMessage(event)
