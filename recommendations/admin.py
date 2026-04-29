from django.contrib import admin
from .models import SearchLog


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "raw_query", "result_count", "latency_ms", "created_at")
    list_filter = ("created_at",)
    search_fields = ("raw_query", "normalized_query", "user__username")