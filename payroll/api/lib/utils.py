import calendar
from datetime import date


def get_date_range(working_date):
    if working_date.day > 15:
        start_date = date(working_date.year, working_date.month, 16)
        end_date = working_date.replace(day=calendar.monthrange(working_date.year, working_date.month)[1])
    else:
        start_date = date(working_date.year, working_date.month, 1)
        end_date = date(working_date.year, working_date.month, 15)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
