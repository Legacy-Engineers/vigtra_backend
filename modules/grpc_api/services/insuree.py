from django_socio_grpc import generics
from modules.insuree.models import Insuree
from ..serializers import InsureeProtoSerializer


class InsureeListService(generics.AsyncReadOnlyModelService):
    queryset = Insuree.objects.all()
    serializer_class = InsureeProtoSerializer
