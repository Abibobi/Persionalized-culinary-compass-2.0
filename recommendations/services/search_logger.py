from recommendations.models import SearchLog


def log_search(*, user, raw_query, normalized_query, parsed_filters, result_count, latency_ms, source):
    return SearchLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        raw_query=raw_query,
        normalized_query=normalized_query,
        parsed_filters=parsed_filters,
        result_count=result_count,
        latency_ms=max(int(latency_ms), 0),
        source=source,
    )
