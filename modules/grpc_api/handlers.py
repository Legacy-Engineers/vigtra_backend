from django_socio_grpc.services.app_handler_registry import AppHandlerRegistry
from modules.grpc_api.services import InsureeListService


def grpc_handlers(server):
    app_registry = AppHandlerRegistry("grpc_api", server)
    app_registry.register(InsureeListService)
