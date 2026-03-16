
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


def calculate_growth_percentile(weight, height):
    if weight < 5:
        return 10
    elif weight > 20:
        return 95
    else:
        return 50


def check_milestone_delay(expected_age, achieved_age):
    return achieved_age > expected_age


def check_immunization_delay(scheduled_date):
    return datetime.now().date() > scheduled_date

def check_who_growth(age_months, weight, height):

    closest_age = min(WHO_STANDARDS.keys(), key=lambda x: abs(x-age_months))
    standard = WHO_STANDARDS[closest_age]

    weight_status = "Normal"
    height_status = "Normal"

    if weight < standard["weight"] * 0.9:
        weight_status = "Underweight"

    if height < standard["height"] * 0.9:
        height_status = "Stunted"

    return weight_status, height_status


def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)

    if bmi < 14:
        status = "Severely Underweight"
    elif bmi < 16:
        status = "Underweight"
    elif bmi < 18:
        status = "Normal"
    else:
        status = "Overweight"

    return round(bmi, 2), status


