import re

DIET_KEYWORDS = {
    "vegan": "vegan",
    "vegetarian": "vegetarian",
    "pescatarian": "pescatarian",
    "omnivore": "omnivore",
    "gluten free": "gluten_free",
}

MEAL_KEYWORDS = {
    "breakfast": "breakfast",
    "lunch": "lunch",
    "dinner": "dinner",
    "snack": "snack",
}

TIME_PATTERN = re.compile(r"(\d+)\s?(min|mins|minutes)")
CAL_PATTERN = re.compile(r"(\d+)\s?(cal|cals|calories)")


def parse_filters(query: str) -> dict:
    filters = {}

    # diet type
    for key, value in DIET_KEYWORDS.items():
        if key in query:
            filters["diet_type"] = value
            break

    # meal type
    for key, value in MEAL_KEYWORDS.items():
        if key in query:
            filters["meal_type"] = value
            break

    # cooking time
    time_match = TIME_PATTERN.search(query)
    if time_match:
        filters["max_time_min"] = int(time_match.group(1))

    # calories
    cal_match = CAL_PATTERN.search(query)
    if cal_match:
        filters["max_calories"] = int(cal_match.group(1))

    return filters