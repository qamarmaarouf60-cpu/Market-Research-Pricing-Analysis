from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # ── Colonnes affichées dans la liste ──────────────────────────────────────
    list_display = [
        "name",
        "price_value",
        "price_text",
        "source",
        "query",
        "created_at",
    ]

    # ── Filtres dans la colonne de droite ─────────────────────────────────────
    list_filter = ["source", "created_at"]

    # ── Barre de recherche ────────────────────────────────────────────────────
    search_fields = ["name", "query", "source"]

    # ── Tri par défaut ────────────────────────────────────────────────────────
    ordering = ["-created_at"]

    # ── Champs non modifiables depuis l'admin ─────────────────────────────────
    readonly_fields = ["created_at", "updated_at"]

    # ── Nombre de produits par page dans l'admin ──────────────────────────────
    list_per_page = 50