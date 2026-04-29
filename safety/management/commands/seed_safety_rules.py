"""
Seed initial safety rules into the database.

Usage: python manage.py seed_safety_rules
"""

from django.core.management.base import BaseCommand
from safety.models import SafetyRule

RULES = [
    {
        "key": "allergy_peanuts",
        "rule_type": "allergen_contains",
        "condition": {"allergen": "peanuts"},
        "severity": "danger",
        "message_template": "Contains peanuts – declared allergen for your profile.",
    },
    {
        "key": "allergy_dairy",
        "rule_type": "allergen_contains",
        "condition": {"allergen": "dairy"},
        "severity": "danger",
        "message_template": "Contains dairy – declared allergen for your profile.",
    },
    {
        "key": "allergy_gluten",
        "rule_type": "allergen_contains",
        "condition": {"allergen": "gluten"},
        "severity": "danger",
        "message_template": "Contains gluten – declared allergen for your profile.",
    },
    {
        "key": "allergy_shellfish",
        "rule_type": "allergen_contains",
        "condition": {"allergen": "shellfish"},
        "severity": "danger",
        "message_template": "Contains shellfish – declared allergen for your profile.",
    },
    {
        "key": "allergy_eggs",
        "rule_type": "allergen_contains",
        "condition": {"allergen": "eggs"},
        "severity": "danger",
        "message_template": "Contains eggs – declared allergen for your profile.",
    },
    {
        "key": "diabetic_high_carbs",
        "rule_type": "nutrient_threshold",
        "condition": {"nutrient": "carbs", "max_value": 60, "health_condition": "diabetic"},
        "severity": "warning",
        "message_template": "High carbs ({value}g > {threshold}g) – may not suit diabetic diet.",
    },
    {
        "key": "diabetic_high_sugar",
        "rule_type": "nutrient_threshold",
        "condition": {"nutrient": "sugar_g", "max_value": 15, "health_condition": "diabetic"},
        "severity": "warning",
        "message_template": "High sugar ({value}g > {threshold}g) – may not suit diabetic diet.",
    },
    {
        "key": "hypertension_sodium",
        "rule_type": "nutrient_threshold",
        "condition": {"nutrient": "sodium_mg", "max_value": 600, "health_condition": "hypertension"},
        "severity": "warning",
        "message_template": "High sodium ({value}mg > {threshold}mg) – may not suit hypertension.",
    },
    {
        "key": "shellfish_allergy_ingredient",
        "rule_type": "ingredient_conflict",
        "condition": {"ingredient": "shrimp", "health_condition": "shellfish allergy"},
        "severity": "danger",
        "message_template": "Contains shrimp (shellfish) – dangerous for shellfish allergy.",
    },
    {
        "key": "shellfish_allergy_crab",
        "rule_type": "ingredient_conflict",
        "condition": {"ingredient": "crab", "health_condition": "shellfish allergy"},
        "severity": "danger",
        "message_template": "Contains crab (shellfish) – dangerous for shellfish allergy.",
    },
]


class Command(BaseCommand):
    help = "Seed initial safety rules"

    def handle(self, *args, **options):
        created_count = 0
        for rule_data in RULES:
            _, created = SafetyRule.objects.update_or_create(
                key=rule_data["key"],
                defaults=rule_data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created_count} new rules ({len(RULES)} total)")
        )
