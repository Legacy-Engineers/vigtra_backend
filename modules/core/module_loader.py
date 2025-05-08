import os
import pathlib

PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

OPENIMIS_MODULES = [
    {
        "name": "insuree",
        "module": "modules.openimis_modules.insuree",
    },
    {
        "name": "policy",
        "module": "modules.openimis_modules.policy",
    },
]
