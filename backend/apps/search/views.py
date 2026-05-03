from rest_framework.views import APIView
from rest_framework.response import Response
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer
from .models import SearchQuery
from rest_framework.permissions import IsAuthenticated

class GlobalSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if query:
            # Enregistrer la recherche dans la base de données
            SearchQuery.objects.create(
                user=request.user if request.user.is_authenticated else None,
                query=query
            )
            
            # Chercher dans les produits (nom ou description)
            products = Product.objects.filter(name__icontains=query)
            serializer = ProductListSerializer(products, many=True)
            
            return Response({
                "query": query,
                "count": products.count(),
                "results": serializer.data
            })
            
        return Response({"message": "Veuillez entrer un mot-clé"}, status=400)
    

class SearchHistoryView(APIView):
    """
    GET /api/search/history/

    Retourne l'historique des recherches
    de l'utilisateur connecté.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        searches = (
            SearchQuery.objects
            .filter(user=request.user)
            .order_by("-created_at")
        )

        results = [
            {
                "id": search.id,
                "query": search.query,
                "created_at": search.created_at,
            }
            for search in searches
        ]

        return Response({
            "count": len(results),
            "results": results
        })