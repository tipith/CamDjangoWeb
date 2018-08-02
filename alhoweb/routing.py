from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from alhopics.consumers import WSConsumer

application = ProtocolTypeRouter({
    # Channels will do this for you automatically. It's included here as an example.
    # "http": AsgiHandler,

    'websocket': AuthMiddlewareStack(URLRouter([path("chat/", WSConsumer),])),
})