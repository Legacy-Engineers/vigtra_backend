class BaseConverter:
    @classmethod
    def to_fhir_obj(cls, obj, reference_type):
        raise NotImplementedError(
            "`toFhirObj()` must be implemented."
        )  # pragma: no cover

    def to_vigtra_obj(cls, obj, user):
        raise NotImplementedError(
            "`toVigtraObj()` must be implemented."
        )  # pragma: no cover
