from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.AskQuestionView.as_view(), name='ask_question'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
]
