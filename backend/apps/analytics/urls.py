from django.urls import path
from .views import (
    GlobalStatsView,
    DistributionView,
    AnalyzeView,
    ScrapeAndAnalyzeView,
    JobStatusView,
)

urlpatterns = [
    path('stats/',          GlobalStatsView.as_view(),      name='analytics-stats'),
    path('distribution/',   DistributionView.as_view(),     name='analytics-distribution'),
    path('analyze/',        AnalyzeView.as_view(),          name='analytics-analyze'),
    path('scrape-analyze/', ScrapeAndAnalyzeView.as_view(), name='analytics-scrape-analyze'),
    path('job-status/',     JobStatusView.as_view(),        name='analytics-job-status'),
]