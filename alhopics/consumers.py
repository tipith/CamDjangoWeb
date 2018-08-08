import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


logger = logging.getLogger(__name__)


class WSConsumer(JsonWebsocketConsumer):

    upgroup = 'camtransport_cam'
    downgroup = 'camtransport_www'

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(WSConsumer.downgroup, self.channel_name)
        self.accept()

    def receive_json(self, content):
        logger.info(content)
        msg = {
            'type': 'command',
            'message': content
        }
        async_to_sync(self.channel_layer.group_send)(WSConsumer.upgroup, msg)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(WSConsumer.downgroup, self.channel_name)

    def live_picture(self, event):
        self.send_json(event['message'])

    def message(self, event):
        self.send_json(event['message'])
