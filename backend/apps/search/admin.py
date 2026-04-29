from django.contrib import admin
from .models import SearchQuery

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    # Les colonnes à afficher dans la liste
    list_display = ('query', 'user', 'created_at')
    
    # Ajouter un filtre latéral pour la date et l'utilisateur
    list_filter = ('created_at', 'user')
    
    # Ajouter une barre de recherche pour chercher dans les mots-clés
    search_fields = ('query',)
    
    # Empêcher la modification des recherches (optionnel, pour l'intégrité des stats)
    readonly_fields = ('created_at',)
