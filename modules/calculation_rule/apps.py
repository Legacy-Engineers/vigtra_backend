from django.apps import AppConfig


class CalculationRuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.calculation_rule"

    def ready(self):
        from .cal_config import CalculationConfigManager

        print("Running the initial for calrule")
        CalculationConfigManager().initial()
