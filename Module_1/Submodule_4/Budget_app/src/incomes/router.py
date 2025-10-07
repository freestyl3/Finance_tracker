from typing import List

from fastapi import APIRouter, Depends

from .schemas import Income
from .dependencies import validate_category

router = APIRouter()
incomes: List[Income] = []

@router.post("/", response_model=Income)
def add_income(income: Income):
    incomes.append(income)
    return income

@router.get("/")
def get_incomes(category: str | None = Depends(validate_category)):

    if category is None:
        if incomes:
            return {
                "incomes": {
                    "total": sum([income.amount for income in incomes]),
                    "data": incomes
                }
            }
        return {"message": "No incomes added"}

    sorted_incomes = [
        income for income in incomes if income.category == category
    ]

    return {
        "incomes": {
            "category": category,
            "total": sum([income.amount for income in sorted_incomes]),
            "data": sorted_incomes
        }
    }
