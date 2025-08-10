import importlib
import inspect
import logging

from django.core.management.base import BaseCommand
from modules.core.module_loader import MODULES
from modules.core.base_demo_generator import BaseDemoDataGenerator


class Command(BaseCommand):
    help = "Generate demo data for all enabled modules"

    def handle(self, *args, **options):
        for module_config in MODULES:
            if not module_config.enabled:
                continue

            module_name = module_config.name
            base_path = module_config.module
            demo_module_path = f"{base_path}.demo_data_generator"

            try:
                mod = importlib.import_module(demo_module_path)
            except ModuleNotFoundError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {module_name} — no demo_data_generator found"
                    )
                )
                continue

            # Find a subclass of BaseDemoDataGenerator
            generator_class = None
            for _, obj in inspect.getmembers(mod, inspect.isclass):
                if (
                    issubclass(obj, BaseDemoDataGenerator)
                    and obj is not BaseDemoDataGenerator
                ):
                    generator_class = obj
                    break

            if not generator_class:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {module_name} — no subclass of BaseDemoDataGenerator found"
                    )
                )
                continue

            try:
                self.stdout.write(
                    self.style.SUCCESS(f"Generating demo data for {module_name}")
                )
                generator = generator_class()
                generator.run_demo()
                self.stdout.write(
                    self.style.SUCCESS(f"Demo data generated for {module_name}")
                )
            except Exception as e:
                logging.exception(e)
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to generate demo data for {module_name}: {e}"
                    )
                )
                break  # stop execution if one fails
