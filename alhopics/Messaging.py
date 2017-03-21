import zmq
import threading
import pickle
import logging
from . Message import Message

module_logger = logging.getLogger('Messaging')


class BaseMessaging(threading.Thread):

    def __init__(self, up, down):
        threading.Thread.__init__(self)
        self.is_running = True
        self.handlers = {}
        self.up = up
        self.down = down

    def run(self):
        if self.down is not None:
            module_logger.info('started')
            while self.is_running:
                msg = self.wait()
                if Message.verify(msg):
                    if msg['id'] in self.handlers:
                        module_logger.info('received %s' % Message.msg_info(msg))
                        self.handlers[msg['id']](msg)
                    else:
                        module_logger.info('no handler found for frame %i' % (msg['id']))
                    if '*' in self.handlers:
                        self.handlers['*'](msg)
            self.down.close()
            module_logger.info('stopped')
        else:
            module_logger.info('no downlink socket given. not starting receive thread')

    def wait(self):
        try:
            return self.down.recv_pyobj()
        except pickle.UnpicklingError as e:
            module_logger.info('Error: UnpicklingError')
            return None
        except (AttributeError, EOFError, ImportError, IndexError) as e:
            module_logger.info('Error: Other')
            return None
        except Exception as e:
            return None

    def send(self, msg):
        if self.up is not None:
            try:
                return self.up.send_pyobj(msg, protocol=2)
            except zmq.ZMQError:
                module_logger.info('Error: unable to send msg')
                return None
        else:
            module_logger.info('no uplink socket given. unable to send message')

    def install(self, frame, handler):
        self.handlers[frame] = handler

    def stop(self):
        self.is_running = False
        if self.up is not None:
            self.up.close()


class LocalClientMessaging(BaseMessaging):

    def __init__(self):
        self.context = zmq.Context()
        outgoing = "tcp://127.0.0.1:9997"

        uplink = self.context.socket(zmq.PUSH)
        uplink.connect(outgoing)

        # module_logger.info('connecting to %s (LocalClient)' % outgoing)
        super(LocalClientMessaging, self).__init__(uplink, None)
