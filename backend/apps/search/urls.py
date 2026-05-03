from django.urls import path
from .views import GlobalSearchView, SearchHistoryView

urlpatterns = [
    path('', GlobalSearchView.as_view(), name='global-search'),
    path("history/", SearchHistoryView.as_view(), name="search-history" ),
]