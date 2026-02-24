# exp_colis/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Voyage, Demande, Correspondance


class CorrespondanceMatchingTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('voyageur1', password='pass123')
        self.user2 = User.objects.create_user('expediteur1', password='pass123')

    def test_voyage_creates_match(self):
        """A new voyage should auto-match an existing compatible demande."""
        Demande.objects.create(
            user=self.user2,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_livraison=date.today() + timedelta(days=3),
            poids=5
        )
        voyage = Voyage.objects.create(
            voyageur=self.user1,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_depart=date.today(),
            date_arrivee=date.today() + timedelta(days=5),
            poids_disponible=10
        )
        self.assertEqual(Correspondance.objects.count(), 1)

    def test_no_self_match(self):
        """A voyageur should not be matched with their own demande."""
        Demande.objects.create(
            user=self.user1,  # same user as voyageur below
            ville_depart='Paris', ville_arrivee='Lyon',
            date_livraison=date.today() + timedelta(days=3),
            poids=5
        )
        Voyage.objects.create(
            voyageur=self.user1,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_depart=date.today(),
            date_arrivee=date.today() + timedelta(days=5),
            poids_disponible=10
        )
        self.assertEqual(Correspondance.objects.count(), 0)

    def test_no_duplicate_correspondance(self):
        """Creating two voyages for the same match should not create duplicates."""
        demande = Demande.objects.create(
            user=self.user2,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_livraison=date.today() + timedelta(days=3),
            poids=5
        )
        voyage = Voyage.objects.create(
            voyageur=self.user1,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_depart=date.today(),
            date_arrivee=date.today() + timedelta(days=5),
            poids_disponible=10
        )
        # Manually call find_matches again (simulates a re-save scenario)
        voyage.find_matches()
        self.assertEqual(Correspondance.objects.count(), 1)

    def test_correspondance_same_user_raises_error(self):
        """Correspondance between the same user's voyage and demande should raise ValidationError."""
        demande = Demande.objects.create(
            user=self.user1,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_livraison=date.today() + timedelta(days=3),
            poids=5
        )
        voyage = Voyage.objects.create(
            voyageur=self.user1,
            ville_depart='Paris', ville_arrivee='Lyon',
            date_depart=date.today(),
            date_arrivee=date.today() + timedelta(days=5),
            poids_disponible=10
        )
        with self.assertRaises(ValidationError):
            Correspondance.objects.create(demande=demande, voyage=voyage)


class ViewAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='pass123')

    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('exp_colis:dashboard'))
        self.assertRedirects(response, f'/accounts/login/?next=/')

    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('exp_colis:dashboard'))
        self.assertEqual(response.status_code, 200)

