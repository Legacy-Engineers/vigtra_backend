from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.identifier import Identifier


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
