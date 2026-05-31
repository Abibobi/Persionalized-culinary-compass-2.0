from django.contrib import admin

from .models import SafetyRule


@admin.register(SafetyRule)
class SafetyRuleAdmin(admin.ModelAdmin):
	list_display = ("key", "rule_type", "severity", "is_active")
	list_filter = ("rule_type", "severity", "is_active")
	search_fields = ("key", "message_template")
