from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Modèle de service/unité : nom, description, responsable (utilisateur).
class Departement(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departements_responsables",
    )

    # Texte lisible quand on affiche l’objet (ex. admin Django).
    def __str__(self):
        return self.nom


# Utilisateur de l’application avec un rôle et (optionnellement) un département.
class Employe(AbstractUser):
    ROLES = [
        ("admin", "Administrateur"),
        ("chief", "Chief"),
        ("plant manager", "Plant Manager"),
        ("manager", "Manager"),
        ("ingenieur", "Ingénieur"),
        ("technicien", "Technicien"),
        ("coordinateur", "Coordinateur"),
        ("superviseur", "Superviseur"),
    ]
    # AbstractUser fournit déjà username, first_name, last_name, email...
    nom = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLES)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True, blank=True)

    # Affiche “Nom complet (rôle)” pour faciliter la lecture.
    def __str__(self):
        base = (self.get_full_name() or f"{self.first_name} {self.last_name}".strip()
                or self.nom or self.username)
        return f"{base} ({self.role})"


# Spécialisation d’Employe pour les superviseurs (force le rôle à “superviseur”).
class Superviseur(Employe):
    """Sous-classe multi-table d’Employe. PK partagée avec Employe."""
    class Meta:
        verbose_name = "Superviseur"
        verbose_name_plural = "Superviseurs"

    # Garantit que le rôle est toujours “superviseur” à l’enregistrement.
    def save(self, *args, **kwargs):
        self.role = "superviseur"
        super().save(*args, **kwargs)
