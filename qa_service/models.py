from django.db import models
import uuid

class QueryLog(models.Model):
    trace_id = models.UUIDField(default=uuid.uuid4, unique=True)
    question = models.TextField()
    answer = models.TextField()
    citations = models.JSONField(default=list)
    tools_used = models.JSONField(default=list)
    retrieval_used = models.BooleanField(default=False)
    duration_ms = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']