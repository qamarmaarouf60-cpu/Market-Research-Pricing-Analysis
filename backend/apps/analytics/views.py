from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from apps.products.models import Product
from data_mining.statistics.descriptive import calculate_distribution

class GlobalStatsView(APIView):
    def get(self, request):
        # Statistiques par Source (Amazon, Jumia, etc.)
        stats = Product.objects.values('source').annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            total=Count('id')
        )
        return Response({"by_source": stats})

class DistributionView(APIView):
    def get(self, request):
        data = Product.objects.all()
        # Calcul des quartiles via script DM
        dist = calculate_distribution(data)
        return Response(dist)