import datetime as dt
import calendar

def get_month_boundaries(year: int, month: int) -> tuple[dt.date, dt.date]:
    _, last_day = calendar.monthrange(year, month)
    return dt.date(year, month, 1), dt.date(year, month, last_day)