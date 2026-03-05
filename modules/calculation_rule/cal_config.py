import pathlib
from dataclasses import dataclass
from modules.core.config_manager import BASE_DIR
import yaml

CALCULATION_RULE_CONFIG_FILE = pathlib.Path(BASE_DIR).joinpath(
    "calculation_rule.config.yaml"
)


@dataclass
class CalculationConfigModelDef:
    name: str
    uuid: str
    description: str
    module: str
    enable: bool = True


DEFAULT_CONFIG = [
    CalculationConfigModelDef(
        name="Income",
        uuid="uuiassseasassss",
        description="Just testing based on income",
        module="vigtra_income_calrule",
        enable=True,
    )
]


class CalculationConfigManager:
    """This is not to be stored in the database"""

    @classmethod
    def initial(cls):
        if not CALCULATION_RULE_CONFIG_FILE.exists():
            cls.load_configuration()

    @classmethod
    def load_configuration(cls):
        with open(CALCULATION_RULE_CONFIG_FILE, "w") as file:
            yaml.safe_dump([vars(entry) for entry in DEFAULT_CONFIG], file)
