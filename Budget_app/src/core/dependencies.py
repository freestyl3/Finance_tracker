from typing import Type
from enum import Enum

from fastapi import Query, HTTPException, status

def make_category_validator(
        category_enum: Type[Enum], description: str | None
    ):
    def validate_category(
            category: str | None = Query(None, description=description)
        ):

        if category is None:
            return None
        
        try:
            return category_enum(category.capitalize())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"Category {category} does not exists",
                    "available_categories": [
                        category.value for category in category_enum
                    ]
                }
            )
        
    return validate_category
