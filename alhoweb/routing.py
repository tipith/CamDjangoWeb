from django.urls import path
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from alhopics.consumers import WSConsumer

application = ProtocolTypeRouter({
    "http": AuthMiddlewareStack(AsgiHandler),
    'websocket': AuthMiddlewareStack(URLRouter([path("chat/", WSConsumer),])),
})