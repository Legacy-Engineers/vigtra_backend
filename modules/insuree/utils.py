import uuid


def generate_insuree_chf_id(prefix: str = "CHF"):
    return prefix + str(uuid.uuid4())[:10]
