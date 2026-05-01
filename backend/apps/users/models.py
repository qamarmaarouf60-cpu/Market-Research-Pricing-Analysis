from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Tu peux ajouter des champs personnalisés ici plus tard
    # Exemple : bio = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.username