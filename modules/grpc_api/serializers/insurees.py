from django_socio_grpc import proto_serializers
from modules.insuree.models import Insuree


class InsureeProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Insuree
        fields = "__all__"
