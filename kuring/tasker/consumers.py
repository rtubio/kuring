
from asgiref.sync import async_to_sync
from channels.generic import websocket
import json
import logging

from common import time as _time
from tasker import models, tasks

_l = logging.getLogger(__name__)


class Tasker(websocket.AsyncJsonWebsocketConsumer):

    _clients = {}

    async def connect(self):

        try:

            taskpk = self.scope['url_route']['kwargs']['taskpk']
            if taskpk in self._clients:
                _l.warning(f"<{taskpk}> client is already connected, multiple connections are not allowed")
                return

            self._clients[taskpk] = {'timestamp_connected': _time.timestamp()}
            await self.channel_layer.group_add('kuring', self.channel_name)
            await self.accept()
            _l.info(f'Accepted connection for task <{taskpk}>')

        except KeyError as ex:
            _l.error(f"The call did not include the task key, cannot accept connection")

    async def disconnect(self, close_code):

        try:

            taskpk = self.scope['url_route']['kwargs']['taskpk']
            if taskpk in self._clients:
                del self._clients[taskpk]
                _l.warning(f"<{taskpk}> client got disconnected")
                return

        except KeyError as ex:
            _l.error(f"The call did not include the task key")
            return

        await self.channel_layer.group_discard('kuring', self.channel_name)

    async def receive(self, text_data):
        _l.debug(f'> text_data = {text_data}')
        message = json.loads(text_data)['message']
        type = message['type']

        if type == 'ping':
            await self.sendMessage({'type': 'pong', 'taskpk': message['taskpk']})
            return
        if type == 'runTask':
            task_obj = tasks.collectData.delay(message['taskpk'])
            await models.taskLaunched(message['taskpk'], task_obj.id)
            return
        if type == 'stopTask':
            await models.taskFinished(message['taskpk'], abort=True)
            return
        if type == 'reportDelay':
            tasks.saveDelay.delay(message['taskpk'], message['t'], message['d'], message['j'])
            return
        if type == 'requestPlot':
            tasks.sendPlot.delay(message['taskpk'], message['sensor'])
            return

    async def sendMessage(self, message):
        if 'taskpk' not in message:
            _l.debug(f"This message does not include <taskpk>, dropping <{message}>")
            return
        if message['taskpk'] not in self._clients:
            _l.debug(f"<{message['taskpk']}> is not a registered client, dropping message <{message}>")
            return
        await self.send(text_data=json.dumps({'message': message}))

    async def event_rx(self, event):
        event['type'] = 'notify.event'
        await self.sendMessage(event)

    async def plot_data(self, event):
        await self.sendMessage(event)

    async def data_rx(self, event):
        # _l.warning(f"Data received = {event}")
        event['type'] = 'plot.data'
        await self.sendMessage(event)

    async def replay_data(self, event):
        await self.sendMessage(event)

    async def task_finished(self, event):
        await self.sendMessage(event)
        await models.taskFinished(event['taskpk'])
