from django.db.models          import Avg, Min, Max, Count
from rest_framework            import status
from rest_framework.decorators import action
from rest_framework.response   import Response
from rest_framework.viewsets   import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from .models      import Product
from .serializers import ProductSerializer, ProductListSerializer


# ── Classe de pagination personnalisée ────────────────────────────────────────
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        On surcharge cette méthode pour garder exactement la même structure 
        JSON que ton ancienne pagination manuelle (pour ne pas casser le frontend React).
        """
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'pages': self.page.paginator.num_pages,
            'results': data
        })


class ProductViewSet(ModelViewSet):
    """
    ViewSet complet pour les produits.

    Endpoints automatiques (via DefaultRouter) :
      GET    /api/products/          → liste paginée
      POST   /api/products/          → créer un produit
      GET    /api/products/{id}/     → détail d'un produit
      PUT    /api/products/{id}/     → modifier un produit
      DELETE /api/products/{id}/     → supprimer un produit

    Endpoints supplémentaires :
      GET    /api/products/stats/    → statistiques des prix
      GET    /api/products/sources/  → liste des sources disponibles
    """

    queryset           = Product.objects.all()
    serializer_class   = ProductSerializer
    pagination_class   = StandardResultsSetPagination

    # ── Sélection du serializer selon l'action ────────────────────────────────
    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer   # version allégée pour les listes
        return ProductSerializer           # version complète pour les détails

    # ── Filtrage, recherche et tri ────────────────────────────────────────────
    def get_queryset(self):
        qs = Product.objects.all()

        # 1. Filtre par source  →  ?source=Jumia
        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source__iexact=source)

        # 2. Filtre par requête de recherche  →  ?query=laptop
        query = self.request.query_params.get("query")
        if query:
            qs = qs.filter(query__icontains=query)

        # 3. Recherche dans le nom  →  ?search=hp
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        # 4. Filtre par plage de prix  →  ?min_price=500&max_price=3000
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            qs = qs.filter(price_value__gte=min_price)
        if max_price:
            qs = qs.filter(price_value__lte=max_price)

        # 5. Tri  →  ?ordering=price_value  ou  ?ordering=-price_value
        ordering = self.request.query_params.get("ordering", "-created_at")
        allowed  = ["price_value", "-price_value", "name", "-name",
                    "created_at", "-created_at"]
        if ordering in allowed:
            qs = qs.order_by(ordering)

        return qs

    # ── Pagination DRF propre ─────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ── Endpoint : statistiques des prix ─────────────────────────────────────
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = self.get_queryset()

        if not qs.exists():
            return Response(
                {"detail": "Aucun produit trouvé pour ces critères."},
                status=status.HTTP_404_NOT_FOUND,
            )

        agg = qs.aggregate(
            avg_price = Avg("price_value"),
            min_price = Min("price_value"),
            max_price = Max("price_value"),
            count     = Count("id"),
        )

        # Répartition par source
        by_source = (
            qs.values("source")
              .annotate(count=Count("id"), avg=Avg("price_value"))
              .order_by("-count")
        )

        # Répartition par gamme de prix
        low     = qs.filter(price_value__lt=1000).count()
        mid     = qs.filter(price_value__gte=1000, price_value__lt=5000).count()
        premium = qs.filter(price_value__gte=5000).count()

        return Response({
            "total":      agg["count"],
            "avg_price":  round(float(agg["avg_price"] or 0), 2),
            "min_price":  float(agg["min_price"] or 0),
            "max_price":  float(agg["max_price"] or 0),
            "by_source":  list(by_source),
            "by_category": {
                "Bas":     low,
                "Moyen":   mid,
                "Premium": premium,
            },
        })

    # ── Endpoint : liste des sources disponibles ──────────────────────────────
    @action(detail=False, methods=["get"], url_path="sources")
    def sources(self, request):
        sources = (
            Product.objects.values("source")
                            .annotate(count=Count("id"))
                            .order_by("-count")
        )
        return Response(list(sources))