from django import forms
from .models import Voyage, Demande, Profile


class VoyageForm(forms.ModelForm):
    date_depart = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_arrivee = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Voyage
        fields = ['ville_depart', 'ville_arrivee', 'date_depart', 'date_arrivee', 'poids_disponible', 'prix_par_kg']
        widgets = {
            'ville_depart': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_arrivee': forms.TextInput(attrs={'class': 'form-control'}),
            'poids_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_par_kg': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_depart = cleaned_data.get('date_depart')
        date_arrivee = cleaned_data.get('date_arrivee')
        if date_depart and date_arrivee and date_arrivee < date_depart:
            raise forms.ValidationError("La date d'arrivée doit être après la date de départ.")
        return cleaned_data


class DemandeForm(forms.ModelForm):
    date_livraison = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Demande
        fields = ['ville_depart', 'ville_arrivee', 'date_livraison', 'poids', 'description']
        widgets = {
            'ville_depart': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_arrivee': forms.TextInput(attrs={'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'ville', 'pays', 'bio', 'photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+237 6XX XXX XXX'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Parlez de vous...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
