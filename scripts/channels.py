from asgiref.sync import async_to_sync
import channels.layers

cl = channels.layers.get_channel_layer()
async_to_sync(cl.send)('test_channel', {'type': 'hello'})
async_to_sync(cl.receive)('test_channel')
