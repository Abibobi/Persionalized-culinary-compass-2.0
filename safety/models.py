from django.db import models


class SafetyRule(models.Model):
	RULE_TYPES = [
		("allergen_contains", "Allergen Contains"),
		("nutrient_threshold", "Nutrient Threshold"),
		("diet_violation", "Diet Violation"),
		("ingredient_conflict", "Ingredient Conflict"),
	]

	SEVERITIES = [
		("info", "Info"),
		("warning", "Warning"),
		("danger", "Danger"),
	]

	key = models.CharField(max_length=100, unique=True)
	rule_type = models.CharField(max_length=30, choices=RULE_TYPES, default="allergen_contains")
	condition = models.JSONField(
		default=dict,
		help_text=(
			"Rule condition definition. Examples:\n"
			'  Allergen: {"allergen": "peanuts"}\n'
			'  Nutrient: {"nutrient": "carbs", "max_value": 60, "health_condition": "diabetic"}\n'
			'  Diet: {"diet": "vegan", "check": "is_vegetarian"}\n'
			'  Ingredient: {"ingredient": "shellfish", "health_condition": "shellfish allergy"}'
		),
	)
	severity = models.CharField(max_length=10, choices=SEVERITIES, default="warning")
	message_template = models.TextField(
		help_text="Warning message template. Use {recipe_name}, {allergen}, {nutrient}, {value}, {threshold}, etc.",
	)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["severity", "key"]

	def __str__(self):
		return f"{self.key} ({self.severity})"
