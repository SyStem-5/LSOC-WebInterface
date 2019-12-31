from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path

from project01 import consumers

application = ProtocolTypeRouter({
    # http->django views is added by default
    'websocket': AuthMiddlewareStack(
        URLRouter([
            #url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.DefaultConsumer),
            path('ws_user/dashboard', consumers.Dashboard),
            path('ws_staff/node_registration', consumers.StaffNodeRegister),
            path('ws_staff/account_management', consumers.StaffAccountManagement),
            path('ws_staff/node_control_panel', consumers.StaffNodeControlPanel),
            path('ws_staff/zones', consumers.StaffZones),
            path('ws_staff/system_status', consumers.StaffSystemStatus),
        ])
    ),
})
