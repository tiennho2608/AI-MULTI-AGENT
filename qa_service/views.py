import time
import uuid
from datetime import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .agent import TechnicalAgent
from .serializers import AskQuestionSerializer, HealthSerializer, MetricsSerializer
from .models import QueryLog
import logging

logger = logging.getLogger(__name__)

# Global metrics storage (in production, use Redis or database)
class MetricsStore:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.tool_calls = 0
        self.retrieval_calls = 0
        self.response_times = []
    
    def record_request(self, duration_ms, tools_used, retrieval_used):
        self.total_requests += 1
        self.tool_calls += len(tools_used)
        if retrieval_used:
            self.retrieval_calls += 1
        self.response_times.append(duration_ms)
    
    def get_metrics(self):
        return {
            "total_requests": self.total_requests,
            "tool_calls": self.tool_calls,
            "retrieval_calls": self.retrieval_calls,
            "avg_response_time_ms": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "uptime_seconds": int(time.time() - self.start_time)
        }

# Global instance
metrics_store = MetricsStore()

class AskQuestionView(APIView):
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.agent = TechnicalAgent()
    
    def post(self, request):
        trace_id = uuid.uuid4()
        start_time = time.time()
        
        logger.info(f"Processing question request - trace_id: {trace_id}")
        
        try:
            serializer = AskQuestionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid input", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            question = serializer.validated_data['question']
            context = serializer.validated_data.get('context', '')
            
            # Process with timeout (simple approach)
            try:
                result = self.agent.process_question(question, context)
            except Exception as e:
                logger.error(f"Agent processing failed - trace_id: {trace_id}, error: {str(e)}")
                return Response(
                    {"error": "Processing failed", "trace_id": str(trace_id)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log the query
            try:
                QueryLog.objects.create(
                    trace_id=trace_id,
                    question=question,
                    answer=result['answer'],
                    citations=result['citations'],
                    tools_used=result['tools_used'],
                    retrieval_used=result['retrieval_used'],
                    duration_ms=int(duration_ms)
                )
            except Exception as e:
                logger.error(f"Failed to log query - trace_id: {trace_id}, error: {str(e)}")
            
            # Update metrics
            metrics_store.record_request(
                duration_ms, 
                result['tools_used'], 
                result['retrieval_used']
            )
            
            response_data = {
                "answer": result['answer'],
                "citations": result['citations'],
                "trace_id": str(trace_id),
                "trace": result['trace']
            }
            
            logger.info(f"Question processed successfully - trace_id: {trace_id}, duration: {duration_ms:.2f}ms")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Unexpected error - trace_id: {trace_id}, error: {str(e)}")
            return Response(
                {"error": "Internal server error", "trace_id": str(trace_id)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HealthView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Basic health checks
            health_data = {
                "status": "ok",
                "timestamp": timezone.now()
            }
            
            serializer = HealthSerializer(health_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class MetricsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            metrics = metrics_store.get_metrics()
            serializer = MetricsSerializer(metrics)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {str(e)}")
            return Response(
                {"error": "Failed to retrieve metrics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
