from django.urls import path
from . import views
from .views import create_employe, liste_employes, modifier_employe, supprimer_employe
urlpatterns = [
   path('accueil/', views.accueil, name='accueil'),
   path('liste/', liste_employes, name='liste_employes'),
   path('ajouter/', create_employe, name='ajouter_employe'),
   path('modifier/<int:id>/', modifier_employe, name='modifier_employe'),
   path('supprimer/<int:id>/', supprimer_employe, name='supprimer_employe'),
   path('departements/', views.liste_departements, name='liste_departements'),
   path('departement/ajouter/', views.ajouter_departement, name='ajouter_departement'),
   path('departement/<int:pk>/modifier/', views.modifier_departement, name='modifier_departement'),
   path('departement/<int:pk>/supprimer/', views.supprimer_departement, name='supprimer_departement'),
   path('departement/<int:pk>/', views.detail_departement, name='detail_departement'),
]
