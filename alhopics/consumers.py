import base64
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from . import Messaging, Message

logger = logging.getLogger(__name__)


class WSConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.messenger = Messaging.LocalClient()
        self.messenger.start()
        self.messenger.install(Message.Message.Image, self.img_callback)
        self.messenger.install('*', self.any_callback)
        self.messenger.send(Message.CommandMessage('joined from', self.channel_name))
        async_to_sync(self.channel_layer.group_add)('debug', self.channel_name)
        logger.info('opened')
        self.accept()

    def receive_json(self, content):
        async_to_sync(self.channel_layer.group_send)('debug', {'text': content['text']})

    def disconnect(self, code):
        self.messenger.send(Message.CommandMessage('disconnect', 'yep'))
        self.messenger.stop()
        async_to_sync(self.channel_layer.group_discard)('debug', self.channel_name)

    def img_callback(self, msg):
        if msg['type'] == Message.ImageMessage.TYPE_LIVE:
            ws_msg = {'livepic': base64.b64encode(msg['data']), 'source': msg['src']}
            self.send_json(ws_msg)
            logger.info('livestream pic from %s' % msg['src'])

    def any_callback(self, msg):
        ws_msg = {'text': Message.Message.msg_info(msg)}
        self.send_json(ws_msg)
        logger.info('any_callback: ' + str(ws_msg))
