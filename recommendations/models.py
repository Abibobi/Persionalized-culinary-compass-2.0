from django.conf import settings
from django.db import models


class SearchLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    raw_query = models.TextField()
    normalized_query = models.TextField()
    parsed_filters = models.JSONField(default=dict, blank=True)
    result_count = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Search {self.id} - {self.raw_query[:40]}"