import uuid


def generate_medical_code() -> str:
    return "MED-" + str(uuid.uuid4())[:8].upper()
