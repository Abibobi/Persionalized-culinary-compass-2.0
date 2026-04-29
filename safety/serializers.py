from rest_framework import serializers
from .models import SafetyRule


class SafetyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyRule
        fields = ("id", "key", "rule_type", "severity", "message_template", "is_active")


class RecipeWarningSerializer(serializers.Serializer):
    rule_key = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
