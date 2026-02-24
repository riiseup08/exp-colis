from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Correspondance, Demande, Voyage, Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Correspondance)
def send_notification(sender, instance, created, **kwargs):
    if instance.colis_pris_en_charge:
        send_mail(
            'Colis Pris en Charge',
            'Le voyageur a pris en charge votre colis.',
            settings.EMAIL_HOST_USER,
            [instance.demande.user.email],
            fail_silently=True,
        )
    if instance.paiement_effectue:
        send_mail(
            'Paiement Effectué',
            'Le client a effectué le paiement pour votre voyage.',
            settings.EMAIL_HOST_USER,
            [instance.voyage.voyageur.email],
            fail_silently=True,
        )


@receiver(post_save, sender=Voyage)
def create_voyage_matches(sender, instance, created, **kwargs):
    if created:
        instance.find_matches()


@receiver(post_save, sender=Demande)
def create_demande_matches(sender, instance, created, **kwargs):
    if created:
        instance.find_matches()
