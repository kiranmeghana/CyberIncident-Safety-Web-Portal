from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from portal import views as portal_views

# --- core/urls.py ---

# 1. NON-TRANSLATED URLS (Remove the duplicates from here)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin-panel/', portal_views.admin_dashboard_view, name='admin_dashboard'),
    path('chatbot/', include('chatbot.urls')),
    path('api/extract/', portal_views.api_extract_image, name='api_extract'),
    
    # REMOVE THESE TWO LINES BELOW:
    # path('dashboard/', portal_views.user_dashboard_view, name='user_dashboard'), 
    # path('profile/', portal_views.profile_settings_view, name='profile_settings'),
]

# 2. TRANSLATED URLS (Keep them here only)
urlpatterns += i18n_patterns(
    path('', portal_views.landing_view, name='landing'),
    path('services/', portal_views.services_view, name='services'),
    path('resources/', portal_views.resources_view, name='resources'),
    path('contact/', portal_views.contact_view, name='contact'),
    path('report/', portal_views.report_incident, name='report_incident'),
    
    # These are the correct ones that support switching:
    path('dashboard/', portal_views.user_dashboard_view, name='user_dashboard'), 
    path('profile/', portal_views.profile_settings_view, name='profile_settings'),
    path('admin-panel/users/', portal_views.user_directory_view, name='admin_user_management'),
    path('admin-panel/analytics/', portal_views.admin_analytics_view, name='admin_analytics'),
    path('admin-panel/ai-core/', portal_views.ai_monitor_view, name='admin_ai_monitor'),

    path('accounts/', include('accounts.urls')),
    prefix_default_language=False,
)

# --------------------------------------------------
# STATIC & MEDIA FILES (DEV ONLY)
# --------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
