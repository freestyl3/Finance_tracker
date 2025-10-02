from typing import List

from fastapi import APIRouter, HTTPException, status, Query

from .schemas import Income, IncomeCategory

router = APIRouter()
incomes: List[Income] = []

@router.post("/", response_model=Income)
def add_income(income: Income):
    incomes.append(income)
    return income

@router.get("/")
def get_incomes(
        category: str | None= Query(None, description="Категория дохода")
    ):

    if category is None:
        if incomes:
            return {
                "incomes": {
                    "total": sum([income.amount for income in incomes]),
                    "data": incomes
                }
            }
        return {"message": "No incomes added"}

    try:
        category_enum = IncomeCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Category {category} does not exists",
                "available_categories": [
                    category.value for category in IncomeCategory
                ]
            }
        )
    
    sorted_incomes = [
        income for income in incomes if income.category == category_enum
    ]

    return {
        "incomes": {
            "category": category,
            "total": sum([income.amount for income in sorted_incomes]),
            "data": sorted_incomes
        }
    }
