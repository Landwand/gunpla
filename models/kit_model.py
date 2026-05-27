from pydantic import BaseModel, field_validator, ValidationInfo, ValidationError # what about other kinds of errors, or is this the only one to consider?
from typing import Optional
import string


class KitModel(BaseModel):
    """Replaces manual validation (previous has_error f'n) with Pydantic"""
    
    # Required Fields
    name: str
    owner_id: int
    condition: str = "new"
    material: str = "plastic"
    
    # Optional w defaults
    grade: Optional[str] = None
    scale: Optional[float] = None
    notes: Optional[str] = None


    @field_validator('scale')
    @classmethod
    def get_scale_from_grade(cls, value, info: ValidationInfo):

        if value is None:
            if info.data.get('grade'):
                users_grade =  info.data.get('grade').strip().lower()
                print(f"DEBUG: users_grade = '{users_grade}'")
            else:
                return value

            match users_grade:
                case "hg":
                    print("DEBUG: Matched HG, returning 144")
                    new_scale = 144
                case "mg":
                    new_scale = 100
                case "pg":
                    new_scale = 60
                case _:
                    new_scale = value  # unknown Grade & Scale, return original Scale 

            return new_scale
        
        else:
            return value  





