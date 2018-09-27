
from channels.routing import ProtocolTypeRouter, URLRouter
import raidikalu.routing


application = ProtocolTypeRouter({
  'websocket': URLRouter(
    raidikalu.routing.websocket_urlpatterns
  ),
})
