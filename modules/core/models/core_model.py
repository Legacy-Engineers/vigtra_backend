from .abstract_models import UUIDModel, ExtendableModel, BaseVersionedModel, BaseCodeModel
# from simple_history

class VigtraCoreModel(BaseCodeModel, BaseVersionedModel, UUIDModel, ExtendableModel):

    class Meta:
        abstract=True


class VigtraHistoryModel(VigtraCoreModel):
    pass