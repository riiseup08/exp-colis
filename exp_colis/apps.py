from django.apps import AppConfig


class ExpColisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exp_colis'

    def ready(self):
        import exp_colis.signals
