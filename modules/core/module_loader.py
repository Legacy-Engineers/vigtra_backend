import os
import pathlib

PARENT_DIR = pathlib.Path(__file__).resolve().parent.parent

MODULES = [
        {
        "name": "insuree",
        "module": "modules.insuree",
    },
    {
        "name": "policy",
        "module": "modules.policy",
    },
]