from rest_framework import serializers
from .models import SearchLog


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()


class SearchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchLog
        fields = (
            "id",
            "raw_query",
            "normalized_query",
            "parsed_filters",
            "result_count",
            "latency_ms",
            "created_at",
        )


class SearchResponseSerializer(serializers.Serializer):
    search_log_id = serializers.IntegerField()
    normalized_query = serializers.CharField()
    parsed_filters = serializers.DictField()
    results = serializers.ListField()
    warnings = serializers.ListField()