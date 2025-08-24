from typing import Dict, Any, Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from modules.location.models import HealthFacility, HealthFacilityType, Location


class HealthFacilityService:
    """Service class for HealthFacility and HealthFacilityType operations."""

    @staticmethod
    def create_health_facility_type(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new health facility type."""
        try:
            with transaction.atomic():
                facility_type = HealthFacilityType.objects.create(
                    name=data["name"],
                    description=data.get("description"),
                    is_active=data.get("is_active", True),
                )

                return {
                    "success": True,
                    "data": {
                        "id": facility_type.id,
                        "name": facility_type.name,
                        "description": facility_type.description,
                        "is_active": facility_type.is_active,
                        "created_at": facility_type.created_at,
                        "updated_at": facility_type.updated_at,
                    },
                    "message": "Health facility type created successfully",
                }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to create health facility type",
            }

    @staticmethod
    def update_health_facility_type(
        facility_type_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing health facility type."""
        try:
            with transaction.atomic():
                facility_type = HealthFacilityType.objects.get(id=facility_type_id)

                if "name" in data:
                    facility_type.name = data["name"]
                if "description" in data:
                    facility_type.description = data["description"]
                if "is_active" in data:
                    facility_type.is_active = data["is_active"]

                facility_type.save()

                return {
                    "success": True,
                    "data": {
                        "id": facility_type.id,
                        "name": facility_type.name,
                        "description": facility_type.description,
                        "is_active": facility_type.is_active,
                        "created_at": facility_type.created_at,
                        "updated_at": facility_type.updated_at,
                    },
                    "message": "Health facility type updated successfully",
                }
        except HealthFacilityType.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility type with the specified ID does not exist"
                ],
                "message": "Health facility type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to update health facility type",
            }

    @staticmethod
    def delete_health_facility_type(facility_type_id: int) -> Dict[str, Any]:
        """Delete a health facility type if it's not in use."""
        try:
            with transaction.atomic():
                facility_type = HealthFacilityType.objects.get(id=facility_type_id)

                # Check if any health facilities are using this type
                if facility_type.healthfacility_set.exists():
                    return {
                        "success": False,
                        "error_details": [
                            "Facility type is in use by existing health facilities"
                        ],
                        "message": "Cannot delete health facility type",
                    }

                facility_type.delete()

                return {
                    "success": True,
                    "data": {"id": facility_type_id},
                    "message": "Health facility type deleted successfully",
                }
        except HealthFacilityType.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility type with the specified ID does not exist"
                ],
                "message": "Health facility type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to delete health facility type",
            }

    @staticmethod
    def create_health_facility(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new health facility."""
        try:
            with transaction.atomic():
                facility_type = HealthFacilityType.objects.get(
                    id=data["facility_type_id"]
                )
                location = Location.objects.get(id=data["location_id"])

                facility = HealthFacility.objects.create(
                    code=data["code"],
                    name=data["name"],
                    facility_type=facility_type,
                    location=location,
                    description=data.get("description"),
                    address=data.get("address"),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    is_active=data.get("is_active", True),
                    established_date=data.get("established_date"),
                )

                return {
                    "success": True,
                    "data": {
                        "id": facility.id,
                        "code": facility.code,
                        "name": facility.name,
                        "facility_type": facility.facility_type.name,
                        "location": facility.location.name,
                        "description": facility.description,
                        "address": facility.address,
                        "phone": facility.phone,
                        "email": facility.email,
                        "is_active": facility.is_active,
                        "established_date": facility.established_date.isoformat()
                        if facility.established_date
                        else None,
                        "created_date": facility.created_date,
                        "last_modified": facility.last_modified,
                    },
                    "message": "Health facility created successfully",
                }
        except HealthFacilityType.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility type with the specified ID does not exist"
                ],
                "message": "Health facility type not found",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to create health facility",
            }

    @staticmethod
    def update_health_facility(
        facility_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing health facility."""
        try:
            with transaction.atomic():
                facility = HealthFacility.objects.get(id=facility_id)

                if "code" in data:
                    facility.code = data["code"]
                if "name" in data:
                    facility.name = data["name"]
                if "facility_type_id" in data:
                    facility_type = HealthFacilityType.objects.get(
                        id=data["facility_type_id"]
                    )
                    facility.facility_type = facility_type
                if "location_id" in data:
                    location = Location.objects.get(id=data["location_id"])
                    facility.location = location
                if "description" in data:
                    facility.description = data["description"]
                if "address" in data:
                    facility.address = data["address"]
                if "phone" in data:
                    facility.phone = data["phone"]
                if "email" in data:
                    facility.email = data["email"]
                if "is_active" in data:
                    facility.is_active = data["is_active"]
                if "established_date" in data:
                    facility.established_date = data["established_date"]

                facility.save()

                return {
                    "success": True,
                    "data": {
                        "id": facility.id,
                        "code": facility.code,
                        "name": facility.name,
                        "facility_type": facility.facility_type.name,
                        "location": facility.location.name,
                        "description": facility.description,
                        "address": facility.address,
                        "phone": facility.phone,
                        "email": facility.email,
                        "is_active": facility.is_active,
                        "established_date": facility.established_date.isoformat()
                        if facility.established_date
                        else None,
                        "created_date": facility.created_date,
                        "last_modified": facility.last_modified,
                    },
                    "message": "Health facility updated successfully",
                }
        except HealthFacility.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility with the specified ID does not exist"
                ],
                "message": "Health facility not found",
            }
        except HealthFacilityType.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility type with the specified ID does not exist"
                ],
                "message": "Health facility type not found",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to update health facility",
            }

    @staticmethod
    def delete_health_facility(facility_id: int) -> Dict[str, Any]:
        """Delete a health facility."""
        try:
            with transaction.atomic():
                facility = HealthFacility.objects.get(id=facility_id)

                # Check if facility is referenced by other models (you may need to add more checks based on your models)
                # For now, we'll just delete it

                facility.delete()

                return {
                    "success": True,
                    "data": {"id": facility_id},
                    "message": "Health facility deleted successfully",
                }
        except HealthFacility.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility with the specified ID does not exist"
                ],
                "message": "Health facility not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to delete health facility",
            }

    @staticmethod
    def get_facilities_by_location(location_id: int) -> Dict[str, Any]:
        """Get all health facilities in a specific location and its descendants."""
        try:
            location = Location.objects.get(id=location_id)

            # Get all descendant locations including the current one
            location_ids = location.get_descendants(include_self=True).values_list(
                "id", flat=True
            )

            facilities = HealthFacility.objects.filter(
                location_id__in=location_ids, is_active=True
            ).select_related("facility_type", "location")

            return {
                "success": True,
                "data": {
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "code": location.code,
                    },
                    "facilities": [
                        {
                            "id": facility.id,
                            "code": facility.code,
                            "name": facility.name,
                            "facility_type": facility.facility_type.name,
                            "location": facility.location.name,
                            "address": facility.address,
                            "phone": facility.phone,
                            "email": facility.email,
                            "is_active": facility.is_active,
                            "established_date": facility.established_date.isoformat()
                            if facility.established_date
                            else None,
                        }
                        for facility in facilities
                    ],
                    "total_count": facilities.count(),
                },
                "message": "Health facilities retrieved successfully",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to retrieve health facilities",
            }

    @staticmethod
    def get_facilities_by_type(facility_type_id: int) -> Dict[str, Any]:
        """Get all health facilities of a specific type."""
        try:
            facility_type = HealthFacilityType.objects.get(id=facility_type_id)

            facilities = HealthFacility.objects.filter(
                facility_type=facility_type, is_active=True
            ).select_related("facility_type", "location")

            return {
                "success": True,
                "data": {
                    "facility_type": {
                        "id": facility_type.id,
                        "name": facility_type.name,
                        "description": facility_type.description,
                    },
                    "facilities": [
                        {
                            "id": facility.id,
                            "code": facility.code,
                            "name": facility.name,
                            "location": facility.location.name,
                            "address": facility.address,
                            "phone": facility.phone,
                            "email": facility.email,
                            "is_active": facility.is_active,
                            "established_date": facility.established_date.isoformat()
                            if facility.established_date
                            else None,
                        }
                        for facility in facilities
                    ],
                    "total_count": facilities.count(),
                },
                "message": "Health facilities retrieved successfully",
            }
        except HealthFacilityType.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Health facility type with the specified ID does not exist"
                ],
                "message": "Health facility type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to retrieve health facilities",
            }
