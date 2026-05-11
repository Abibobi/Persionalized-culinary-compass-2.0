from .allergy_check import check_allergies
from .diet_check import check_diet


def run_safety_checks(user_profile, recipe):
    warnings = []
    warnings.extend(check_allergies(user_profile, recipe))
    warnings.extend(check_diet(user_profile, recipe))
    return warnings