from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    # ── Champ calculé : catégorie de prix ─────────────────────────────────────
    price_category = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            "id",
            "name",
            "price_text",
            "price_value",
            "price_category",   #  champ calculé
            "source",
            "url",
            "image_url",
            "query",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]  #  protégés

    # ── Logique du champ calculé ──────────────────────────────────────────────
    def get_price_category(self, obj) -> str:
        return obj.price_category

    # ── Validation ────────────────────────────────────────────────────────────
    def validate_price_value(self, value):
        """Le prix ne peut pas être négatif ou nul."""
        if value <= 0:
            raise serializers.ValidationError(
                "Le prix doit être strictement positif."
            )
        return value

    def validate_name(self, value):
        """Le nom ne peut pas être une chaîne vide."""
        if not value.strip():
            raise serializers.ValidationError(
                "Le nom du produit ne peut pas être vide."
            )
        return value.strip()


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer allégé pour les listes (moins de données = réponse plus rapide).
    Utilisé dans le tableau du dashboard React.
    """
    price_category = serializers.ReadOnlyField()

    class Meta:
        model  = Product
        fields = [
            "id",
            "name",
            "price_value",
            "price_category",
            "source",
            "url",
            "image_url",
        ]