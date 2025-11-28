from typing import Dict, Optional, List
import json


def vigtra_message(
    success: bool = False,
    message: str = "",
    data: dict | None = "",
    error_details: str = "",
    validation_errors: Optional[Dict] = None,
    error_code: Optional[Dict] = None,
    correlation_id: Optional[str] = None,
    execution_time: Optional[float] = None,
    affected_objects: Optional[List[Dict]] = None,
) -> Dict[str, bool | dict | str]:
    """
    Function to create a message dictionary for VIGTRA API responses.

    Args:
        success (bool): Indicates if the operation was successful.
        message (str): Message to be included in the response.
        data (dict | None): Additional data to be included in the response.

    Returns:
        dict: A dictionary containing the success status, message, and data.
    """
    if not message:
        raise ValueError("In a vigtra message sender, Message cannot be empty")

    if not success:
        if not error_details:
            raise ValueError(
                "In a vigtra message sender, Error details cannot be empty"
            )

        if not isinstance(error_details, list):
            return TypeError("The error details must be a list")

    return {
        "success": success,
        "message": message,
        "data": data,
        "error_details": error_details,
        "validation_errors": validation_errors,
        "error_code": error_code,
        "correlation_id": correlation_id,
        "execution_time": execution_time,
        "affected_objects": affected_objects,
    }


def get_data_from_file(file_path: str, file_type: str) -> dict:
    """
    Function to read data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Data read from the JSON file.
    """

    if file_type == "json":
        with open(file_path, "r") as file:
            data = json.load(file)
        return data

    else:
        raise ValueError("File type not supported. Only JSON files are supported.")


def save_file_from_base64(file_base64: str, output_path: str) -> str:
    try:
        print("Testing")

    except Exception as exce:
        raise Exception(f"Failed to save file due to an unhandled error: {exce}")


def prefix_filterset(prefix, filterset):
    if type(filterset) is dict:
        return {(prefix + k): v for k, v in filterset.items()}
    elif type(filterset) is list:
        return [(prefix + x) for x in filterset]
    else:
        return filterset
