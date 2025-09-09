from django.urls import path
from . import views

urlpatterns = [
    path('absence/nouveau/', views.absence_new, name='absence_new'),
    path('absence/', views.absence_list, name='absence_list'),
    path('absence/<int:pk>/modifier/', views.absence_edit, name='absence_edit'),
    path("absence/<int:pk>/delete/", views.absence_delete, name="absence_delete"),
]
