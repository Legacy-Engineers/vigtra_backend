from typing import Dict
import json

def vigtra_message(success: bool = False, message: str = "", data: dict | None = "", error_details: str = "" ) -> Dict[str, bool | dict | str]:
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
            raise ValueError("In a vigtra message sender, Error details cannot be empty")

    return {
        "success": success,
        "message": message,
        "data": data,
        "error_details": error_details
    }


def get_data_from_file(file_path: str, file_type: str)-> dict:
    """
    Function to read data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Data read from the JSON file.
    """


    if file_path == 'json':
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    
    else:
        raise ValueError("File type not supported. Only JSON files are supported.")