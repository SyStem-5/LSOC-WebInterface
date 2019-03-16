from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path

from project01 import consumers

application = ProtocolTypeRouter({
    # http->django views is added by default
    'websocket': AuthMiddlewareStack(
        URLRouter([
            #url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.DefaultConsumer),
            path('', consumers.DefaultConsumer),
            path('superuser', consumers.SuperuserConsumer),
        ])
    ),
})