from modules.authentication.services.data_loader_service import DataLoaderService

MODEL_DATA = [
    {
        "name": "Group Model Data Loader",
        "service": lambda: DataLoaderService().load_groups()
    }
]