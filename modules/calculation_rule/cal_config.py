from typing import List, Dict, Optional
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
        CALCULATION_RULE_CONFIG_FILE.mkdir(exist_ok=True)
        with open(CALCULATION_RULE_CONFIG_FILE) as file:
            yaml.safe_dump(DEFAULT_CONFIG, file)
