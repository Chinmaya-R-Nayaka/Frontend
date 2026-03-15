
from datetime import datetime

WHO_STANDARDS = {
    6: {"weight": 7.9, "height": 67},
    12: {"weight": 9.6, "height": 76},
    24: {"weight": 12.2, "height": 87},
    36: {"weight": 14.3, "height": 96},
    48: {"weight": 16.3, "height": 103}
}


def calculate_age_in_months(dob):
    days_difference = (datetime.now() - datetime.combine(dob, datetime.min.time())).days
    return days_difference // 30
