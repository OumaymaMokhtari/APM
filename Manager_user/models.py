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
        related_name="departements_responsables" 
    )
    def __str__(self):
        return self.nom
class Employe(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('chief', 'Chief'),
        ('plant manager', 'Plant Manager'),
        ('manager', 'Manager'),
        ('ingenieur', 'Ingénieur'),
        ('technicien', 'Technicien'),   
        ('coordinateur', 'Coordinateur')
    ]
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLES)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"

class Service(models.Model):
    nom = models.CharField(max_length=100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"{self.nom} ({self.departement.nom})"

class Poste(models.Model):
    nom = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='postes')

    def __str__(self):
        return f"{self.nom} ({self.service.nom})"
