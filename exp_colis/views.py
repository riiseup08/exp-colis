from .models import Voyage, Demande, Correspondance, Profile
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
import smtplib

from .forms import VoyageForm, DemandeForm, ProfileForm


@login_required
def home_view(request):
    voyages = Voyage.objects.filter(voyageur=request.user).order_by('-created_at')
    demandes = Demande.objects.filter(user=request.user).order_by('-created_at')
    correspondances = Correspondance.objects.filter(
        models.Q(demande__user=request.user) |
        models.Q(voyage__voyageur=request.user)
    ).select_related('demande', 'voyage').order_by('-date_correspondance')
    return render(request, 'voyages/dashboard.html', {
        'voyages': voyages,
        'demandes': demandes,
        'correspondances': correspondances
    })


@login_required
def add_voyage(request):
    if request.method == 'POST':
        form = VoyageForm(request.POST)
        if form.is_valid():
            voyage = form.save(commit=False)
            voyage.voyageur = request.user
            voyage.save()
            messages.success(request, "Voyage ajouté avec succès!")
            return redirect('exp_colis:dashboard')
    else:
        form = VoyageForm()
    return render(request, 'voyages/add_voyage.html', {'form': form})


@login_required
def add_demande(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.user = request.user
            demande.save()
            messages.success(request, "Demande ajoutée avec succès!")
            return redirect('exp_colis:dashboard')
    else:
        form = DemandeForm()
    return render(request, 'voyages/add_demande.html', {'form': form})

@login_required
def edit_voyage(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id, voyageur=request.user)
    if request.method == 'POST':
        form = VoyageForm(request.POST, instance=voyage)
        if form.is_valid():
            form.save()
            voyage.find_matches()  # ← ADD THIS LINE
            messages.success(request, "Voyage modifié avec succès!")
            return redirect('exp_colis:dashboard')
    else:
        form = VoyageForm(instance=voyage)
    return render(request, 'voyages/edit_voyage.html', {'form': form})


@login_required
def delete_voyage(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id, voyageur=request.user)
    if request.method == 'POST':
        voyage.delete()
        messages.success(request, "Voyage supprimé.")
        return redirect('exp_colis:dashboard')
    return render(request, 'voyages/confirm_delete.html', {'object': voyage})

@login_required
def edit_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, user=request.user)
    if request.method == 'POST':
        form = DemandeForm(request.POST, instance=demande)
        if form.is_valid():
            form.save()
            demande.find_matches()  # ← ADD THIS LINE
            messages.success(request, "Demande modifiée avec succès!")
            return redirect('exp_colis:dashboard')
    else:
        form = DemandeForm(instance=demande)
    return render(request, 'voyages/edit_demande.html', {'form': form})


@login_required
def delete_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, user=request.user)
    if request.method == 'POST':
        demande.delete()
        messages.success(request, "Demande supprimée.")
        return redirect('exp_colis:dashboard')
    return render(request, 'voyages/confirm_delete.html', {'object': demande})


@login_required
def prendre_colis(request, correspondance_id):
    correspondance = get_object_or_404(Correspondance, id=correspondance_id)
    if request.user == correspondance.voyage.voyageur:
        try:
            correspondance.colis_pris_en_charge = True
            correspondance.save()
            messages.success(request, "Colis pris en charge avec succès.")
            return redirect('exp_colis:dashboard')
        except ValidationError as e:
            return render(request, 'voyages/error_page.html', {'error_message': str(e)})
    else:
        return render(request, 'voyages/error_page.html', {
            'error_message': "Vous n'êtes pas autorisé à prendre en charge ce colis."
        })


@login_required
def effectuer_paiement(request, correspondance_id):
    correspondance = get_object_or_404(Correspondance, id=correspondance_id)
    if request.user == correspondance.demande.user:
        correspondance.paiement_effectue = True
        correspondance.save()
        messages.success(request, "Paiement effectué avec succès.")
        try:
            send_mail(
                'Paiement effectué',
                'Le client a effectué le paiement pour votre voyage.',
                settings.EMAIL_HOST_USER,
                [correspondance.voyage.voyageur.email],
                fail_silently=False,
            )
        except smtplib.SMTPException as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email: {str(e)}")
    else:
        messages.error(request, "Vous n'êtes pas autorisé à effectuer ce paiement.")
    return redirect('exp_colis:dashboard')


@login_required
def validate_correspondance(request, correspondance_id):
    correspondance = get_object_or_404(Correspondance, id=correspondance_id)
    if request.method == 'POST':
        correspondance.is_validated = True
        correspondance.validated_at = timezone.now()
        correspondance.save()
        messages.success(request, "Correspondance validée!")
        return redirect('exp_colis:dashboard')
    return render(request, 'voyages/validate_correspondance.html', {'correspondance': correspondance})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}! Votre compte a été créé.")
            return redirect('exp_colis:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès!")
            return redirect('exp_colis:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'voyages/profile.html', {'form': form, 'profile': profile})


@login_required
def public_profile(request, username):
    from django.contrib.auth.models import User as AuthUser
    user = get_object_or_404(AuthUser, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    voyages = Voyage.objects.filter(voyageur=user).order_by('-created_at')
    demandes = Demande.objects.filter(user=user).order_by('-created_at')
    return render(request, 'voyages/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'voyages': voyages,
        'demandes': demandes,
    })


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès!")
            return redirect('exp_colis:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'voyages/profile.html', {'form': form, 'profile': profile})


@login_required
def public_profile(request, username):
    from django.contrib.auth.models import User as AuthUser
    user = get_object_or_404(AuthUser, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    voyages = Voyage.objects.filter(voyageur=user).order_by('-created_at')
    demandes = Demande.objects.filter(user=user).order_by('-created_at')
    return render(request, 'voyages/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'voyages': voyages,
        'demandes': demandes,
    })


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('exp_colis:dashboard')
    return render(request, 'voyages/landing.html')
