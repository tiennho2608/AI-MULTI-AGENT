from django.contrib import admin
from .models import QueryLog

@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('trace_id', 'question', 'created_at', 'duration_ms', 'retrieval_used')
    list_filter = ('retrieval_used', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('trace_id', 'created_at')
    ordering = ('-created_at',)