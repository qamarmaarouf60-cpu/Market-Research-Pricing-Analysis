from django.contrib import admin
from .models import PriceSnapshot

@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    # Ce qu'on voit dans la liste des rapports
    list_display = ('category', 'avg_price', 'min_price', 'max_price', 'count', 'calculated_at')
    
    # Pouvoir filtrer par catégorie (ex: "Laptops", "Smartphones")
    list_filter = ('category', 'calculated_at')
    
    # Barre de recherche pour retrouver un rapport précis
    search_fields = ('category',)
    
    # On met les champs en lecture seule car ce sont des données calculées
    # On ne veut pas qu'un utilisateur change la moyenne manuellement !
    readonly_fields = ('calculated_at', 'avg_price', 'min_price', 'max_price', 'count')