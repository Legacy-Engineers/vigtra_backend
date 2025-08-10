from modules.core.module_loader import ModuleLoader

module_websocket_urls = ModuleLoader()._get_websockets()

websocket_urlpatterns = []

websocket_urlpatterns.extend(module_websocket_urls)
