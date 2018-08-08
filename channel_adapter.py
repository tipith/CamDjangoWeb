import base64, logging, time

from alhoweb.asgi import channel_layer
from asgiref.sync import async_to_sync

from alhopics import Message, Messaging

# fetching channel_layer sets up logging. clear existing handlers
if logging.root:
    del logging.root.handlers[:]


import base64, logging, time

from alhoweb.asgi import channel_layer
from asgiref.sync import async_to_sync

from alhopics import Message, Messaging

# fetching channel_layer sets up logging. clear existing handlers
if logging.root:
    del logging.root.handlers[:]


class ChannelConnection:

    def __init__(self, upgroup, downgroup, channel):
        self.upgroup = upgroup
        self.downgroup = downgroup
        self.channel = channel
        channel_layer.group_expiry = 365*24*3600
        self._connect()

    def _connect(self):
        async_to_sync(channel_layer.group_add)(self.downgroup, self.channel)
        self.next_refresh = time.time() + channel_layer.group_expiry - 5

    def _refresh_if_needed(self):
        if time.time() > self.next_refresh:
            print('refresh channel')
            self.stop()
            self._connect()

    def get_msg(self):
        self._refresh_if_needed()  # next call will block so this does not work
        msg = async_to_sync(channel_layer.receive)(self.channel)
        return msg['message']

    def send_msg(self, msg):
        async_to_sync(channel_layer.group_send)(self.upgroup, msg)

    def stop(self):
        async_to_sync(channel_layer.group_discard)(self.downgroup, self.channel)


chconn = ChannelConnection(upgroup='camtransport_www', downgroup='camtransport_cam', channel='adapter')


def on_img(msg):
    if msg['type'] == Message.ImageMessage.TYPE_LIVE:
        adapted = {
            'type': 'live_picture',
            'message': {
                'source': msg['src'],
                'livepic': base64.b64encode(msg['data']).decode('ascii')
            }
        }
        chconn.send_msg(adapted)


def on_any(msg):
    adapted = {
        'type': 'message',
        'message': {
            'text': Message.Message.msg_info(msg)
        }
    }
    chconn.send_msg(adapted)
    print(f'to web: {adapted["message"]}')


if __name__ == '__main__':
    messenger = Messaging.LocalClient()
    messenger.install(Message.Message.Image, on_img)
    messenger.install('*', on_any)
    messenger.start()
    messenger.send(Message.CommandMessage('join', 'web'))
    print('started, now adapting messages')

    try:
        while True:
            msg = chconn.get_msg()
            print(f'from web: {msg}')
            if set(msg.keys()).issubset(['command', 'parameter']):
                messenger.send(Message.CommandMessage(**msg))
    finally:
        chconn.stop()
        messenger.send(Message.CommandMessage('disconnect', 'web'))
        messenger.stop()
