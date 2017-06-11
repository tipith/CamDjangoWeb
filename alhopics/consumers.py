from channels import Group
from channels.sessions import channel_session
from alhopics import cam_messenger
import Message


def callback(msg):
    Group("debug").send({"text": Message.Message.msg_info(msg)})
    print 'got %s' + Message.Message.msg_info(msg)


@channel_session
def ws_connect(message):
    cam_messenger.install('*', callback)
    cam_messenger.send(Message.Message.msg_command('joined from', str(message['client'])))
    message.reply_channel.send({"accept": True})
    Group("debug").add(message.reply_channel)


@channel_session
def ws_message(message):
    Group("debug").send({"text": message['text']})


@channel_session
def ws_disconnect(message):
    cam_messenger.send(Message.Message.msg_command('disconnect', 'yep'))
    Group("debug").discard(message.reply_channel)
