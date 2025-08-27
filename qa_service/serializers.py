from rest_framework import serializers

class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)
    context = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")
    
    def validate_question(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Question must be at least 3 characters long")
        # Basic input sanitization
        if any(char in value for char in ['<script', '<?php', '<%']):
            raise serializers.ValidationError("Invalid characters in question")
        return value.strip()

class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()

class MetricsSerializer(serializers.Serializer):
    total_requests = serializers.IntegerField()
    tool_calls = serializers.IntegerField()
    retrieval_calls = serializers.IntegerField()
    avg_response_time_ms = serializers.FloatField()
    uptime_seconds = serializers.IntegerField()