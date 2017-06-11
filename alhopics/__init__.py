import Messaging, Message


def startup():
    global cam_messenger
    cam_messenger = Messaging.LocalClientMessaging()
    cam_messenger.start()
    print 'created ' + str(cam_messenger)


startup()
