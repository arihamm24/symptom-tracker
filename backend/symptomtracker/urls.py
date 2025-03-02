from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, UserProfileView, UserSettingsView,
    ChangePasswordView, LogoutView, PhysicalPainEntryViewSet,
    MentalWellnessEntryViewSet, DiaryEntryViewSet, PhysicianInfoViewSet,
    NotificationViewSet, DataAnalysisView, NotificationSettingsView, HealthAppSettingsView,
    CommunitySettingsView, EmergencyContactView, HomeScreenDataView
)

router = DefaultRouter()
router.register(r'physical-pain', PhysicalPainEntryViewSet, basename='physical-pain')
router.register(r'mental-wellness', MentalWellnessEntryViewSet, basename='mental-wellness')
router.register(r'diary', DiaryEntryViewSet, basename='diary')
router.register(r'physician-info', PhysicianInfoViewSet, basename='physician-info')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'data-analysis', DataAnalysisView, basename='data-analysis')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('settings/notifications/', NotificationSettingsView.as_view(), name='notification_settings'),
    path('settings/health-app/', HealthAppSettingsView.as_view(), name='health_app_settings'),
    path('settings/community/', CommunitySettingsView.as_view(), name='community_settings'),
    path('emergency-contact/', EmergencyContactView.as_view(), name='emergency_contact'),
    path('home-data/', HomeScreenDataView.as_view(), name='home-data'),
]