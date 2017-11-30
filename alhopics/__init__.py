from . import Messaging, Message

cam_messenger = None

def startup():
    global cam_messenger
    if not isinstance(cam_messenger, Messaging.LocalClientMessaging):
        cam_messenger = Messaging.LocalClientMessaging()
        cam_messenger.start()
    print('created ' + str(cam_messenger))


startup()
