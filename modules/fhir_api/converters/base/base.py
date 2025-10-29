import enum


@enum.Enum
class ReferenceTypeEnum:
    pass


class BaseVigtrFhirConverter:
    @classmethod
    def to_fhir_obj(vigtra_obj, reference_type):
        raise NotImplementedError("The `to_fhir_obj()` must be implemented")

    @classmethod
    def to_vigtra_obj(vigtra_obj, reference_type):
        raise NotImplementedError("The `to_vigtra_obj()` must be implemented")

    @classmethod
    def build_fhir_identifier(vigtra_obj, fhir_obj, reference_type):
        if hasattr(vigtra_obj, "uuid"):
            fhir_obj.id = vigtra_obj.uuid
            # fhir_obj.identifier = Iden
