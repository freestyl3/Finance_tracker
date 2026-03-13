import csv
import io
import calendar
from datetime import date

from fastapi import HTTPException, status

from src.reports.schemas import ReportFilter

def generate_csv_report(data: dict) -> io.StringIO:
    output = io.StringIO()

    writer = csv.writer(output, delimiter=';')

    output.write('\ufeff')

    writer.writerow(["Total expenses", str(data["total_sum"]).replace('.', ',')])
    writer.writerow([])

    writer.writerow(["Category ID", "Category name", "Amount"])

    for row in data["categories"]:
        writer.writerow([
            row["category_id"],
            row.get("category_name", "Unknown"),
            str(row["total_amount"]).replace('.', ',')
        ])

    output.seek(0)

    return output

def get_month_range(year: int, month: int) -> tuple[date, date]:
    first_day = date(year, month, 1)

    _, last_day_num = calendar.monthrange(year, month)

    last_day = date(year, month, last_day_num)

    return first_day, last_day

### ДОБАВИТЬ КАСТОМНОЕ ИСКЛЮЧЕНИЕ И ОБРАБОТЧИК

def check_date_order(filters: ReportFilter) -> None | ValueError:
    try:
        filters.check_date_order()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )