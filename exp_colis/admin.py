# exp_colis/admin.py
from django.contrib import admin
from .models import Voyage, Demande, Correspondance


@admin.register(Voyage)
class VoyageAdmin(admin.ModelAdmin):
    list_display = ['voyageur', 'ville_depart', 'ville_arrivee', 'date_depart', 'poids_disponible']
    list_filter = ['ville_depart', 'ville_arrivee']
    search_fields = ['voyageur__username', 'ville_depart', 'ville_arrivee']


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ['user', 'ville_depart', 'ville_arrivee', 'date_livraison', 'poids']
    search_fields = ['user__username', 'ville_depart', 'ville_arrivee']


@admin.register(Correspondance)
class CorrespondanceAdmin(admin.ModelAdmin):
    list_display = ['demande', 'voyage', 'is_validated', 'colis_pris_en_charge', 'paiement_effectue']
    list_filter = ['is_validated', 'colis_pris_en_charge', 'paiement_effectue']
