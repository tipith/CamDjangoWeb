import base64
import json

from channels import Group
from channels.sessions import channel_session
from alhopics import cam_messenger
from . import Message


def img_callback(msg):
    if msg['type'] == 3:
        ws_msg = json.dumps({"livepic": base64.b64encode(msg['data']), "source": msg['src']})
        Group("debug").send({"text": ws_msg})
        print('livestream pic from %s' % msg['src'])


def any_callback(msg):
    ws_msg = json.dumps({"text": Message.Message.msg_info(msg)})
    Group("debug").send({"text": ws_msg})
    print('got %s' + Message.Message.msg_info(msg))


@channel_session
def ws_connect(message):
    cam_messenger.install(Message.Message.Image, img_callback)
    cam_messenger.install('*', any_callback)
    cam_messenger.send(Message.CommandMessage('joined from', str(message['client'])))
    message.reply_channel.send({"accept": True})
    Group("debug").add(message.reply_channel)


@channel_session
def ws_message(message):
    Group("debug").send({"text": message['text']})


@channel_session
def ws_disconnect(message):
    cam_messenger.send(Message.CommandMessage('disconnect', 'yep'))
    Group("debug").discard(message.reply_channel)
