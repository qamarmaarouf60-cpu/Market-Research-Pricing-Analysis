from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer
from .models import SearchQuery
from .serializers import SearchQuerySerializer

class GlobalSearchView(APIView):
    """Recherche globale et enregistrement de l'historique."""
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if query:
            # Enregistrement
            SearchQuery.objects.create(
                user=request.user if request.user.is_authenticated else None,
                query=query
            )
            
            # Recherche icontains (Standard)
            products = Product.objects.filter(name__icontains=query)
            serializer = ProductListSerializer(products, many=True)
            
            return Response({
                "query": query,
                "count": products.count(),
                "results": serializer.data
            })
            
        return Response({"message": "Veuillez entrer un mot-clé"}, status=400)

class SearchHistoryView(APIView):
    """Retourne l'historique via le Serializer (Optimisé)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        searches = SearchQuery.objects.filter(user=request.user).order_by("-created_at")
        # Utilisation directe du serializer pour un code plus propre
        serializer = SearchQuerySerializer(searches, many=True)
        return Response(serializer.data)