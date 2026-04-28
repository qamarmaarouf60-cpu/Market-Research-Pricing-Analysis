from django.db.models         import Avg, Min, Max, Count, StdDev
from rest_framework           import status
from rest_framework.decorators import action
from rest_framework.response  import Response
from rest_framework.viewsets  import ModelViewSet

from .models      import Product
from .serializers import ProductSerializer, ProductListSerializer


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

    # ── Pagination simple ─────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        # Pagination manuelle  →  ?page=1&page_size=20
        try:
            page      = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except ValueError:
            page, page_size = 1, 20

        page_size = min(page_size, 100)     # max 100 par page
        start     = (page - 1) * page_size
        end       = start + page_size
        total     = qs.count()

        serializer = self.get_serializer(qs[start:end], many=True)

        return Response({
            "total":     total,
            "page":      page,
            "page_size": page_size,
            "pages":     (total + page_size - 1) // page_size,
            "results":   serializer.data,
        })

    # ── Endpoint : statistiques des prix ─────────────────────────────────────
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """
        GET /api/products/stats/?query=laptop&source=Jumia

        Retourne les statistiques de prix pour affichage dans le dashboard.
        """
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
            std_price = StdDev("price_value"),
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
            "std_price":  round(float(agg["std_price"] or 0), 2),
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
        """
        GET /api/products/sources/

        Retourne la liste des sources présentes en base.
        Utile pour remplir le filtre "Source" dans React.
        """
        sources = (
            Product.objects.values("source")
                           .annotate(count=Count("id"))
                           .order_by("-count")
        )
        return Response(list(sources))