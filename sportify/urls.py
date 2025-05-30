from django.contrib import admin
from django.urls import path
from registration import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Add root URL pattern for home view
    path('events/', views.event_list, name='event_list'),
    path('events/register/<int:event_id>/', views.register_event, name='register_event'),
    path('coaching/', views.coaching, name='coaching'),
    path('sports_venues/', views.sports_venues, name='sports_venues'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('societies/', views.society_list, name='society_list'),
    path('', views.home, name='home'),
    path('events/register/<int:event_id>/payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
     path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
