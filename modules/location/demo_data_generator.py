from django.db import transaction
from modules.location.models import Location, LocationType
from modules.core.base_demo_generator import BaseDemoDataGenerator
from modules.location import MODULE_DIR
import logging
import os
import json

DEMO_DATA_FILE = os.path.join(MODULE_DIR, "data_files", "demo_locations.json")


logger = logging.getLogger(__name__)


class LocationDemoDataGenerator(BaseDemoDataGenerator):
    def run_demo(self):
        try:
            self.generate_location_types()
            self.generate_country()
            self.generate_states()
            self.generate_districts()
            self.generate_cities()
            self.generate_sub_districts()
            self.generate_villages()
            self.generate_communities()
        except Exception as e:
            logger.error(f"Demo generation stopped due to error: {e}")
            raise  # Stop execution immediately

    def load_demo_data(self) -> dict:
        with open(DEMO_DATA_FILE, "r") as file:
            return json.load(file).get("demo_locations", {})

    @transaction.atomic
    def generate_location_types(self):
        demo_data = self.load_demo_data()
        location_types_data = demo_data.get("location_types", [])

        # Check if location types already exist
        existing_types = LocationType.objects.filter(
            name__in=[lt["name"] for lt in location_types_data]
        )
        if existing_types.exists():
            logger.info(
                f"Location types already exist: {[et.name for et in existing_types]}"
            )
            return

        # Convert dictionaries to LocationType instances
        location_types = []
        for location_type_data in location_types_data:
            location_type = LocationType(
                name=location_type_data["name"], level=location_type_data["level"]
            )
            location_types.append(location_type)

        new_location_types = LocationType.objects.bulk_create(location_types)
        logger.info(f"Location types generated: {len(new_location_types)}")

    @transaction.atomic
    def generate_country(self):
        demo_data = self.load_demo_data()
        country_data = demo_data.get("country", {})

        # Check if country already exists
        if Location.objects.filter(code=country_data.get("code")).exists():
            logger.info(f"Country already exists: {country_data.get('name')}")
            return

        # Get the country location type
        country_type = LocationType.objects.get(name="Country")

        new_country = Location.objects.create(
            name=country_data.get("name"),
            code=country_data.get("code"),
            type=country_type,
        )
        logger.info(f"Country generated: {new_country.name}")

    @transaction.atomic
    def generate_states(self):
        demo_data = self.load_demo_data()
        states_data = demo_data.get("states", [])

        # Get the state location type and parent country
        state_type = LocationType.objects.get(name="State")
        parent_location = Location.objects.get(code="COUNTRY-GMB")

        for state_data in states_data:
            # Check if state already exists
            if Location.objects.filter(code=state_data["code"]).exists():
                logger.info(f"State already exists: {state_data['name']}")
                continue

            state_location = Location.objects.create(
                name=state_data["name"],
                code=state_data["code"],
                type=state_type,
                parent=parent_location,
            )
            logger.info(f"State generated: {state_location.name}")

    @transaction.atomic
    def generate_districts(self):
        demo_data = self.load_demo_data()
        districts_data = demo_data.get("districts", [])

        # Get the district location type
        district_type = LocationType.objects.get(name="District")

        for district_data in districts_data:
            # Check if district already exists
            if Location.objects.filter(code=district_data["code"]).exists():
                logger.info(f"District already exists: {district_data['name']}")
                continue

            # Get parent state by code
            parent_code = district_data["parent_code"]
            try:
                parent_location = Location.objects.get(code=parent_code)
                district_location = Location.objects.create(
                    name=district_data["name"],
                    code=district_data["code"],
                    type=district_type,
                    parent=parent_location,
                )
                logger.info(f"District generated: {district_location.name}")
            except Location.DoesNotExist:
                logger.warning(
                    f"Parent location with code {parent_code} not found for district {district_data['name']}"
                )

    @transaction.atomic
    def generate_cities(self):
        demo_data = self.load_demo_data()
        cities_data = demo_data.get("cities", [])

        # Get the city location type
        city_type = LocationType.objects.get(name="City")

        for city_data in cities_data:
            # Check if city already exists
            if Location.objects.filter(code=city_data["code"]).exists():
                logger.info(f"City already exists: {city_data['name']}")
                continue

            # Get parent district by code
            parent_code = city_data["parent_code"]
            try:
                parent_location = Location.objects.get(code=parent_code)
                city_location = Location.objects.create(
                    name=city_data["name"],
                    code=city_data["code"],
                    type=city_type,
                    parent=parent_location,
                )
                logger.info(f"City generated: {city_location.name}")
            except Location.DoesNotExist:
                logger.warning(
                    f"Parent location with code {parent_code} not found for city {city_data['name']}"
                )

    @transaction.atomic
    def generate_sub_districts(self):
        demo_data = self.load_demo_data()
        sub_districts_data = demo_data.get("sub_districts", [])

        # Get the sub-district location type
        sub_district_type = LocationType.objects.get(name="Sub-District")

        for sub_district_data in sub_districts_data:
            # Check if sub-district already exists by code
            if Location.objects.filter(code=sub_district_data["code"]).exists():
                logger.info(f"Sub-District already exists: {sub_district_data['name']}")
                continue

            # Get parent district by code
            parent_code = sub_district_data["parent_code"]
            try:
                parent_location = Location.objects.get(code=parent_code)

                # Check if sub-district with same name and parent already exists
                if Location.objects.filter(
                    name=sub_district_data["name"], parent=parent_location
                ).exists():
                    logger.info(
                        f"Sub-District with name '{sub_district_data['name']}' already exists under parent '{parent_location.name}'"
                    )
                    continue

                sub_district_location = Location.objects.create(
                    name=sub_district_data["name"],
                    code=sub_district_data["code"],
                    type=sub_district_type,
                    parent=parent_location,
                )
                logger.info(f"Sub-District generated: {sub_district_location.name}")
            except Location.DoesNotExist:
                logger.warning(
                    f"Parent location with code {parent_code} not found for sub-district {sub_district_data['name']}"
                )

    @transaction.atomic
    def generate_villages(self):
        demo_data = self.load_demo_data()
        villages_data = demo_data.get("villages", [])

        # Get the village location type
        village_type = LocationType.objects.get(name="Village")

        for village_data in villages_data:
            # Check if village already exists by code
            if Location.objects.filter(code=village_data["code"]).exists():
                logger.info(f"Village already exists: {village_data['name']}")
                continue

            # Get parent sub-district by code
            parent_code = village_data["parent_code"]
            try:
                parent_location = Location.objects.get(code=parent_code)

                # Check if village with same name and parent already exists
                if Location.objects.filter(
                    name=village_data["name"], parent=parent_location
                ).exists():
                    logger.info(
                        f"Village with name '{village_data['name']}' already exists under parent '{parent_location.name}'"
                    )
                    continue

                village_location = Location.objects.create(
                    name=village_data["name"],
                    code=village_data["code"],
                    type=village_type,
                    parent=parent_location,
                )
                logger.info(f"Village generated: {village_location.name}")
            except Location.DoesNotExist:
                logger.warning(
                    f"Parent location with code {parent_code} not found for village {village_data['name']}"
                )

    @transaction.atomic
    def generate_communities(self):
        demo_data = self.load_demo_data()
        communities_data = demo_data.get("communities", [])

        # Get the community location type
        community_type = LocationType.objects.get(name="Community")

        for community_data in communities_data:
            # Check if community already exists by code
            if Location.objects.filter(code=community_data["code"]).exists():
                logger.info(f"Community already exists: {community_data['name']}")
                continue

            # Get parent village by code
            parent_code = community_data["parent_code"]
            try:
                parent_location = Location.objects.get(code=parent_code)

                # Check if community with same name and parent already exists
                if Location.objects.filter(
                    name=community_data["name"], parent=parent_location
                ).exists():
                    logger.info(
                        f"Community with name '{community_data['name']}' already exists under parent '{parent_location.name}'"
                    )
                    continue

                community_location = Location.objects.create(
                    name=community_data["name"],
                    code=community_data["code"],
                    type=community_type,
                    parent=parent_location,
                )
                logger.info(f"Community generated: {community_location.name}")
            except Location.DoesNotExist:
                logger.warning(
                    f"Parent location with code {parent_code} not found for community {community_data['name']}"
                )
