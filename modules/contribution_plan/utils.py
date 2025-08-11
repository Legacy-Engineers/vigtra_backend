import uuid
from modules.core.config_manager import ConfigManager

contribution_plan_config = ConfigManager.get_contribution_plan_config()


def generate_contribution_plan_code():
    prefix = contribution_plan_config["code_config"]["prefix"]
    length = contribution_plan_config["code_config"]["length"]
    generated_code = f"{prefix}-{str(uuid.uuid4())[:length].upper()}"
    return generated_code
