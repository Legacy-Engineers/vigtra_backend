import os
import pathlib

PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

MODULES = [
    {
        "name": "Insuree",
        "module": "modules.insuree",
    },
    {
        "name": "Policy",
        "module": "modules.policy",
    },
    {
        "name": "Claim",
        "module": "modules.claim",
    },
    {
        "name": "Claim AI",
        "module": "modules.claim.claim_ai",
    },
    {
        "name": "authentication",
        "module": "modules.authentication",
    },
    {
        "name": "Fhir API",
        "module": "modules.fhir_api",
    },
    {
        "name": "Contribution",
        "module": "modules.contribution",
    },
    {
        "name": "Formal Sector",
        "module": "modules.formal_sector",
    },
    {
        "name": "Location",
        "module": "modules.location",
    },
    {
        "name": "Policy",
        "module": "modules.policy",
    },
    {
        "name": "Product",
        "module": "modules.product",
    },
]