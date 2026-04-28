from django.db import models
from decimal import Decimal


class Product(models.Model):

    # ── Choix pour la source ──────────────────────────────────────────────────
    SOURCE_CHOICES = [
        ("Jumia",   "Jumia"),
        ("Avito",   "Avito"),
        ("Amazon",  "Amazon"),
        ("eBay",    "eBay"),
        ("Other",   "Other"),
    ]

    # ── Champs principaux ─────────────────────────────────────────────────────
    name        = models.CharField(max_length=255)
    price_text  = models.CharField(max_length=100)          # "7,975.00 Dhs"
    price_value = models.DecimalField(                      # FloatField → DecimalField
                    max_digits=12,
                    decimal_places=2
                  )
    source      = models.CharField(
                    max_length=100,
                    choices=SOURCE_CHOICES,
                    default="Other"
                  )
    url         = models.URLField(max_length=1000, blank=True, null=True)
    image_url   = models.URLField(max_length=1000, blank=True, null=True)  

    # ── Lien avec la recherche ────────────────────────────────────────────────
    query       = models.CharField(                          
                    max_length=255,
                    blank=True,
                    null=True,
                    help_text="Terme de recherche qui a produit ce produit"
                  )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)       

    # ── Métadonnées Django ────────────────────────────────────────────────────
    class Meta:
        ordering            = ["-created_at"]               # les plus récents en premier
        verbose_name        = "Produit"
        verbose_name_plural = "Produits"
        indexes = [
            models.Index(fields=["source"]),
            models.Index(fields=["query"]),
            models.Index(fields=["price_value"]),
        ]

    def __str__(self):                                       
        return f"{self.name} — {self.price_text} ({self.source})"

    @property
    def price_category(self) -> str:
        """Retourne la catégorie de prix basée sur price_value."""
        price = self.price_value
        if price < Decimal("1000"):
            return "Bas"
        elif price < Decimal("5000"):
            return "Moyen"
        else:
            return "Premium"