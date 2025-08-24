from typing import Dict, Any, Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from modules.location.models import Location, LocationType


class LocationService:
    """Service class for Location and LocationType operations."""

    @staticmethod
    def create_location_type(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new location type."""
        try:
            with transaction.atomic():
                location_type = LocationType.objects.create(
                    name=data["name"], level=data["level"]
                )

                return {
                    "success": True,
                    "data": {
                        "id": location_type.id,
                        "name": location_type.name,
                        "level": location_type.level,
                        "created_at": location_type.created_at,
                        "updated_at": location_type.updated_at,
                    },
                    "message": "Location type created successfully",
                }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to create location type",
            }

    @staticmethod
    def update_location_type(
        location_type_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing location type."""
        try:
            with transaction.atomic():
                location_type = LocationType.objects.get(id=location_type_id)

                if "name" in data:
                    location_type.name = data["name"]
                if "level" in data:
                    location_type.level = data["level"]

                location_type.save()

                return {
                    "success": True,
                    "data": {
                        "id": location_type.id,
                        "name": location_type.name,
                        "level": location_type.level,
                        "created_at": location_type.created_at,
                        "updated_at": location_type.updated_at,
                    },
                    "message": "Location type updated successfully",
                }
        except LocationType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location type with the specified ID does not exist"],
                "message": "Location type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to update location type",
            }

    @staticmethod
    def delete_location_type(location_type_id: int) -> Dict[str, Any]:
        """Delete a location type if it's not in use."""
        try:
            with transaction.atomic():
                location_type = LocationType.objects.get(id=location_type_id)

                # Check if any locations are using this type
                if location_type.location_set.exists():
                    return {
                        "success": False,
                        "error_details": [
                            "Location type is in use by existing locations"
                        ],
                        "message": "Cannot delete location type",
                    }

                location_type.delete()

                return {
                    "success": True,
                    "data": {"id": location_type_id},
                    "message": "Location type deleted successfully",
                }
        except LocationType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location type with the specified ID does not exist"],
                "message": "Location type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to delete location type",
            }

    @staticmethod
    def create_location(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new location."""
        try:
            with transaction.atomic():
                location_type = LocationType.objects.get(id=data["type_id"])

                parent = None
                if data.get("parent_id"):
                    parent = Location.objects.get(id=data["parent_id"])

                location = Location.objects.create(
                    name=data["name"],
                    type=location_type,
                    parent=parent,
                    code=data.get("code"),
                    is_active=data.get("is_active", True),
                )

                return {
                    "success": True,
                    "data": {
                        "id": location.id,
                        "name": location.name,
                        "type": location.type.name,
                        "parent": location.parent.name if location.parent else None,
                        "code": location.code,
                        "is_active": location.is_active,
                        "created_at": location.created_at,
                        "updated_at": location.updated_at,
                    },
                    "message": "Location created successfully",
                }
        except LocationType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location type with the specified ID does not exist"],
                "message": "Location type not found",
            }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": [
                    "Parent location with the specified ID does not exist"
                ],
                "message": "Parent location not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to create location",
            }

    @staticmethod
    def update_location(location_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing location."""
        try:
            with transaction.atomic():
                location = Location.objects.get(id=location_id)

                if "name" in data:
                    location.name = data["name"]
                if "type_id" in data:
                    location_type = LocationType.objects.get(id=data["type_id"])
                    location.type = location_type
                if "parent_id" in data:
                    if data["parent_id"]:
                        parent = Location.objects.get(id=data["parent_id"])
                        location.parent = parent
                    else:
                        location.parent = None
                if "code" in data:
                    location.code = data["code"]
                if "is_active" in data:
                    location.is_active = data["is_active"]

                location.save()

                return {
                    "success": True,
                    "data": {
                        "id": location.id,
                        "name": location.name,
                        "type": location.type.name,
                        "parent": location.parent.name if location.parent else None,
                        "code": location.code,
                        "is_active": location.is_active,
                        "created_at": location.created_at,
                        "updated_at": location.updated_at,
                    },
                    "message": "Location updated successfully",
                }
        except Location.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location with the specified ID does not exist"],
                "message": "Location not found",
            }
        except LocationType.DoesNotExist:
            return {
                "success": False,
                "error_details": ["Location type with the specified ID does not exist"],
                "message": "Location type not found",
            }
        except Exception as e:
            return {
                "success": False,
                "error_details": [str(e)],
                "message": "Failed to update location",
            }

    @staticmethod
    def delete_location(location_id: int) -> Dict[str, Any]:
        """Delete a location if it's not in use."""
        try:
            with transaction.atomic():
                location = Location.objects.get(id=location_id)

                # Check if location has children
                if location.children.exists():
                    return {
                        "success": False,
                        "error_details": [
                            "Location has child locations and cannot be deleted"
                        ],
                        "message": "Cannot delete location",
                    }

                # Check if location is used by health facilities
                if location.healthfacility_set.exists():
                    return {
                        "success": False,
                        "error_details": [
                            "Location is used by health facilities and cannot be deleted"
                        ],
                        "message": "Cannot delete location",
                    }

                location.delete()

                return {
                    "success": True,
                    "data": {"id": location_id},
                    "message": "Location deleted successfully",
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
                "message": "Failed to delete location",
            }

    @staticmethod
    def get_location_hierarchy(location_id: int) -> Dict[str, Any]:
        """Get the complete hierarchy for a location."""
        try:
            location = Location.objects.get(id=location_id)

            ancestors = location.get_ancestors(include_self=True)
            children = location.get_children()
            descendants = location.get_descendants()

            return {
                "success": True,
                "data": {
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "code": location.code,
                        "type": location.type.name,
                        "full_path": location.get_full_path(),
                    },
                    "hierarchy": {
                        "ancestors": [
                            {
                                "id": ancestor.id,
                                "name": ancestor.name,
                                "code": ancestor.code,
                                "type": ancestor.type.name,
                                "level": ancestor.level,
                            }
                            for ancestor in ancestors
                        ],
                        "children": [
                            {
                                "id": child.id,
                                "name": child.name,
                                "code": child.code,
                                "type": child.type.name,
                                "level": child.level,
                            }
                            for child in children
                        ],
                        "descendants_count": descendants.count(),
                    },
                },
                "message": "Location hierarchy retrieved successfully",
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
                "message": "Failed to retrieve location hierarchy",
            }
