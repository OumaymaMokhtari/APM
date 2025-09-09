from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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

    def __str__(self):
        return self.nom

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

    def __str__(self):
        base = (self.get_full_name() or f"{self.first_name} {self.last_name}".strip()
                or self.nom or self.username)
        return f"{base} ({self.role})"


class Superviseur(Employe):
    """Sous-classe multi-table d’Employe. PK partagée avec Employe."""
    class Meta:
        verbose_name = "Superviseur"
        verbose_name_plural = "Superviseurs"

    def save(self, *args, **kwargs):
        self.role = "superviseur"
        super().save(*args, **kwargs)
