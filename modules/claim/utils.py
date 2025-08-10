import random
from modules.core.config_manager import ConfigManager

claim_config = ConfigManager.get_claim_config()


def claim_code_generator():
    code_config = claim_config.get("code_config", {})
    prefix = code_config.get("prefix", "CLM")
    auto_generate = code_config.get("auto_generate", True)
    length = code_config.get("length", 10)

    if auto_generate:
        random_number = random.randint(10 ** (length - 1), 10**length - 1)
        prepared_code = f"{prefix}-{str(random_number).zfill(length)}"
        return prepared_code
    else:
        return None
