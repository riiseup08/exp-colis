from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Voyage(models.Model):
    voyageur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voyages')
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    date_depart = models.DateField()
    date_arrivee = models.DateField()
    poids_disponible = models.PositiveIntegerField()
    prix_par_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voyage de {self.voyageur.username}: {self.ville_depart} → {self.ville_arrivee}"

    def find_matches(self):
        # Match on destination only — ignore dates
        matching_demandes = Demande.objects.filter(
            ville_depart__iexact=self.ville_depart,
            ville_arrivee__iexact=self.ville_arrivee,
            poids__lte=self.poids_disponible
        )
        for demande in matching_demandes:
            if demande.user != self.voyageur:
                Correspondance.objects.get_or_create(
                    demande=demande,
                    voyage=self
                )
                logger.info(f'Correspondance created: voyage {self.id} <-> demande {demande.id}')


class Demande(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes')
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    date_livraison = models.DateField()
    poids = models.FloatField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.user.username}: {self.ville_depart} → {self.ville_arrivee}"

    def find_matches(self):
        # Match on destination only — ignore dates
        matching_voyages = Voyage.objects.filter(
            ville_depart__iexact=self.ville_depart,
            ville_arrivee__iexact=self.ville_arrivee,
            poids_disponible__gte=self.poids
        )
        for voyage in matching_voyages:
            if voyage.voyageur != self.user:
                Correspondance.objects.get_or_create(
                    demande=self,
                    voyage=voyage
                )
                logger.info(f'Correspondance created: demande {self.id} <-> voyage {voyage.id}')


class Correspondance(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE)
    voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE)
    date_correspondance = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    colis_pris_en_charge = models.BooleanField(default=False)
    paiement_effectue = models.BooleanField(default=False)

    class Meta:
        unique_together = ('demande', 'voyage')

    def clean(self):
        if self.demande.user == self.voyage.voyageur:
            raise ValidationError("La correspondance doit être entre deux utilisateurs différents.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Correspondance: [{self.demande}] <-> [{self.voyage}]'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    @property
    def nb_voyages(self):
        return self.user.voyages.count()

    @property
    def nb_demandes(self):
        return self.user.demandes.count()
