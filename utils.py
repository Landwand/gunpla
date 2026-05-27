from typing import Callable, Optional, Union, Tuple, Dict, Any
from flask import jsonify, Response, Request
from pydantic import BaseModel, ValidationError
from models.kit_model import KitModel
import sqlite3  # Import SQLite for database operations


def check_for_json(req):
    if not req.is_json:
        error_message = "Error: data is not JSON."
        return (False, error_message)  # Return a tuple indicating failure
    return (True, None)  # Return a tuple indicating success


def extract_fields(kit: KitModel, exceptions: Optional[list[str]] = None) -> tuple[bool, list[dict[str, Any]] | dict[str, str]]:
    """    
    Extracts fields from a KitModel instance, excluding specified exceptions.

    Args:
        kit (KitModel): The KitModel instance to extract fields from.
        exceptions (Optional[list[str]]): A list of field names to exclude from extraction.

    Returns:
        Union[list[dict[str, str]], dict[str, str]]: A list of extracted fields as dictionaries, or an error dictionary if extraction fails.
    """

    exceptions = exceptions or []
  

    # check count of Exceptions vs fields in KitModel
    kit_dict = kit.model_dump()
    if len(exceptions) >= len(kit_dict):
        return (False, {"error": "Count of Exceptions >= fields in KitModel"})


    '''
    extracted = []
    for k, v in kit_dict.items():
        if k in exceptions:
            pass
        else:
            extracted.append({k:v})
    '''
    # replaces the following with List Comprehension
    extracted = [
        {k: v} for k, v in kit_dict.items() if k not in exceptions
    ]

    if not extracted:
        return (False, {"error":"extracted_fields had nothing to extract."})
    return (True, extracted)


def validate_req_data(
        data: dict,
        model: BaseModel,

        # Optional = a "Union" between Basemodel, None -- # need to expand note.
        # Callable is any object with __call__ method, like a f'n
        # Optional [[]] (two brackets) because Callable can expect a list

        on_success: Optional[Callable[[BaseModel], Any]] = None) -> tuple[bool, Union[BaseModel, dict[str, Any]]]:
    
    try:
        validated_kit_data = KitModel(**data)
        success_check = True
        return (success_check, validated_kit_data)
    except ValidationError as e:
        success_check = False
        validated_kit_data = {
            "message": str(e),  # Human-readable summary of errors
            "details": e.errors()  # Structured error details
        }
        return (success_check, validated_kit_data) # returns errors in multiple formats



# pending replacement by Pydantic
def has_error(inputs):
    app.logger.info("%s has_error started")

    #initilize return values
    is_error = 0 # 1 in case-of error
    msg = "good"
    kit_vals = inputs
        
    name = inputs['name']
    scale = inputs['scale']
    notes = inputs['notes']
    condition = inputs['condition']
    grade = inputs['grade']
    material = inputs['material']
    
    if len(name) < 1:
        msg = "name too short"
        app.logger.info(msg)
        is_error = 1
        return is_error, msg, kit_vals  
    if not condition:
        condition = 'new'
    if not grade:
        grade = None
    if not material:
        material = 'plastic'
    if not notes:
        notes = None

    if not scale:
        match grade:
            case "hg":
                scale = 144
            case "fg":
                scale = 144
            case "rg":
                scale = 144
            case "mg":
                scale = 100
            case "eg":
                scale = 144
            case "pg":
                scale = 60
            case _:
                scale = None

    if scale:
        try:
            if int(scale) < 1:
                is_error = 1
                msg = "scale too small"
                return is_error, msg, kit_vals
        except:
            msg = "ERROR: 'Scale' not a valid number!"
            is_error = 1
            return is_error, msg, kit_vals

    # save corrected form inputs to kit_vals and prep to return
    kit_vals = {}
    for variable in ["name", "scale", "grade", "condition", "material", "notes"]:
        kit_vals[variable] = eval(variable)
    # check_value: 0 = good, 1 = error
    return is_error, msg, kit_vals

# suite of utils for testing

def generate_example_kit(kit=None):
    """Generate an example kit with default and sample values."""

    return {
    "name": "Gundam Alex",
    "owner_id": 1,
    "condition": "new",
    "material": "plastic",
    "grade": "MG",
    "scale": 100,
    "notes": "A classic Master Grade kit."
    }


def setup_test_gunpla_db():
    """Set up an in-memory SQLite database with the gunpla table schema."""
    conn = sqlite3.connect(':memory:')  # Create an in-memory database
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE gunpla (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            condition TEXT NOT NULL,
            material TEXT NOT NULL,
            grade TEXT,
            scale INTEGER,
            notes TEXT
        )
    ''')  # Define the schema
    conn.commit()
    return conn
