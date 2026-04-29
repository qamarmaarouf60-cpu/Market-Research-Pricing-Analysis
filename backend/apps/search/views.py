from rest_framework.views import APIView
from rest_framework.response import Response
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer
from .models import SearchQuery

class GlobalSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        
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