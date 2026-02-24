from django.contrib import admin
from django.urls import path, include
from exp_colis import views as exp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', exp_views.register_view, name='register'),
    path('dashboard/', include('exp_colis.urls')),
    path('', exp_views.landing_page, name='landing'),
]
