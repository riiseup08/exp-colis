from django.urls import path
from .views import (
    home_view, add_voyage, add_demande,
    edit_voyage, delete_voyage,
    edit_demande, delete_demande,
    prendre_colis, effectuer_paiement,
    validate_correspondance,
    profile_view, public_profile
)

app_name = 'exp_colis'

urlpatterns = [
    path('', home_view, name='dashboard'),
    path('add_voyage/', add_voyage, name='add_voyage'),
    path('add_demande/', add_demande, name='add_demande'),
    path('edit_voyage/<int:voyage_id>/', edit_voyage, name='edit_voyage'),
    path('delete_voyage/<int:voyage_id>/', delete_voyage, name='delete_voyage'),
    path('edit_demande/<int:demande_id>/', edit_demande, name='edit_demande'),
    path('delete_demande/<int:demande_id>/', delete_demande, name='delete_demande'),
    path('prendre_colis/<int:correspondance_id>/', prendre_colis, name='prendre_colis'),
    path('effectuer_paiement/<int:correspondance_id>/', effectuer_paiement, name='effectuer_paiement'),
    path('validate_correspondance/<int:correspondance_id>/', validate_correspondance, name='validate_correspondance'),
    path('profile/', profile_view, name='profile'),
    path('profile/<str:username>/', public_profile, name='public_profile'),
]
