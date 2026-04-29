from django.urls import path
from .views import (
    GlobalStatsView, 
    DistributionView
)

urlpatterns = [
    path('stats/', 
         GlobalStatsView.as_view()),
    path('distribution/', 
         DistributionView.as_view()),
]