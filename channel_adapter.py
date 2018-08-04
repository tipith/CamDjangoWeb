import base64, logging

from alhoweb.asgi import channel_layer
from asgiref.sync import async_to_sync

from alhopics import Message, Messaging

if logging.root:
    del logging.root.handlers[:]


def on_img(msg):
    if msg['type'] == Message.ImageMessage.TYPE_LIVE:
        adapted = {
            'type': 'live_picture',
            'message': {
                'source': msg['src'],
                'livepic': base64.b64encode(msg['data']).decode('ascii')
            }
        }
        async_to_sync(channel_layer.group_send)('transport_web', adapted)


def on_any(msg):
    adapted = {
        'type': 'message',
        'message': {
            'text': Message.Message.msg_info(msg)
        }
    }
    async_to_sync(channel_layer.group_send)('transport_web', adapted)
    print(f'to web: {adapted["message"]}')


if __name__ == '__main__':
    messenger = Messaging.LocalClient()
    messenger.install(Message.Message.Image, on_img)
    messenger.install('*', on_any)
    messenger.start()
    messenger.send(Message.CommandMessage('join', 'web'))
    async_to_sync(channel_layer.group_add)('transport_cam', 'adapter')
    print('started, now adapting messages')

    try:
        while True:
            msg = async_to_sync(channel_layer.receive)('adapter')
            contents = msg['message']
            print(f'from web: {contents}')
            if 'command' in contents and 'parameter' in contents:
                messenger.send(Message.CommandMessage(contents['command'], contents['parameter']))
    finally:
        async_to_sync(channel_layer.group_add)('transport_cam', 'adapter')
        messenger.send(Message.CommandMessage('disconnect', 'web'))
        messenger.stop()
