from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.models import User
from .models import (
    PhysicalPainEntry, MentalWellnessEntry, DiaryEntry,
    PhysicianInfo, Notification
)
from .serializers import (
    PhysicalPainEntrySerializer, MentalWellnessEntrySerializer, DiaryEntrySerializer,
    PhysicianInfoSerializer, NotificationSerializer, RegisterSerializer, UserSerializer, 
    UserSettingsSerializer, ChangePasswordSerializer, UserProfileSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
        
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Handle user fields
        user_data = {}
        for field in ['first_name', 'last_name', 'email']:
            if field in request.data:
                user_data[field] = request.data.get(field)
        
        if user_data:
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle profile fields
        if 'profile' in request.data and isinstance(request.data['profile'], dict):
            profile_data = request.data['profile']
            profile_serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Return the updated user
        return Response(UserSerializer(user).data)

class UserSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSettingsSerializer
    
    def get_object(self):
        return self.request.user.settings
    
    def update(self, request, *args, **kwargs):
        # Handle regular settings updates
        settings_serializer = self.get_serializer(
            self.get_object(), 
            data=request.data, 
            partial=True
        )
        settings_serializer.is_valid(raise_exception=True)
        settings_serializer.save()
        
        # Check if username is included in the request
        if 'username' in request.data:
            try:
                user = request.user
                new_username = request.data.get('username')
                
                # Check if username is already taken
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    return Response(
                        {'error': 'This username is already taken.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user.username = new_username
                user.save()
            except Exception as e:
                return Response(
                    {'error': f'Failed to update username: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(UserSerializer(request.user).data)
    
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            # Update session auth hash to keep user logged in
            update_session_auth_hash(request, user)
            
            return Response(
                {"message": "Password updated successfully"}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSettingsSerializer
    
    def get_object(self):
        return self.request.user.settings
    
    def get(self, request, *args, **kwargs):
        settings = self.get_object()
        return Response({
            'notification_enabled': settings.notification_enabled,
            'reminder_frequency': settings.reminder_frequency
        })
    
    def patch(self, request, *args, **kwargs):
        settings = self.get_object()
        
        if 'notification_enabled' in request.data:
            settings.notification_enabled = request.data['notification_enabled']
        
        if 'reminder_frequency' in request.data:
            settings.reminder_frequency = request.data['reminder_frequency']
        
        settings.save()
        
        return Response({
            'notification_enabled': settings.notification_enabled,
            'reminder_frequency': settings.reminder_frequency
        })

class HealthAppSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.settings
    
    def get(self, request, *args, **kwargs):
        settings = self.get_object()
        return Response({
            'health_app_sync': settings.health_app_sync,
            'health_app_type': settings.health_app_type
        })
    
    def patch(self, request, *args, **kwargs):
        settings = self.get_object()
        
        if 'health_app_sync' in request.data:
            settings.health_app_sync = request.data['health_app_sync']
        
        if 'health_app_type' in request.data:
            settings.health_app_type = request.data['health_app_type']
        
        settings.save()
        
        return Response({
            'health_app_sync': settings.health_app_sync,
            'health_app_type': settings.health_app_type
        })

class CommunitySettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.settings
    
    def get(self, request, *args, **kwargs):
        settings = self.get_object()
        return Response({
            'community_enabled': settings.community_enabled,
            'community_username': settings.community_username
        })
    
    def patch(self, request, *args, **kwargs):
        settings = self.get_object()
        
        if 'community_enabled' in request.data:
            settings.community_enabled = request.data['community_enabled']
        
        if 'community_username' in request.data:
            settings.community_username = request.data['community_username']
        
        settings.save()
        
        return Response({
            'community_enabled': settings.community_enabled,
            'community_username': settings.community_username
        })

# For the emergency contact, we'll use a view that returns the emergency contact information
class EmergencyContactView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        return Response({
            'emergency_contact_name': profile.emergency_contact_name,
            'emergency_contact_phone': profile.emergency_contact_phone,
            'emergency_contact_relationship': profile.emergency_contact_relationship
        })
    
class PhysicalPainEntryViewSet(viewsets.ModelViewSet):
    serializer_class = PhysicalPainEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PhysicalPainEntry.objects.filter(user=self.request.user).order_by('-timestamp')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_entries = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_entries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_to_physician(self, request, pk=None):
        entry = self.get_object()
        # Implement email sending logic here
        entry.sent_to_physician = True
        entry.save()
        return Response({'status': 'sent to physician'})

class MentalWellnessEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MentalWellnessEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MentalWellnessEntry.objects.filter(user=self.request.user).order_by('-timestamp')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_entries = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_entries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_to_physician(self, request, pk=None):
        entry = self.get_object()
        # Implement email sending logic here
        entry.sent_to_physician = True
        entry.save()
        return Response({'status': 'sent to physician'})

class DiaryEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DiaryEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-timestamp')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_to_physician(self, request, pk=None):
        entry = self.get_object()
        # Implement email sending logic here
        entry.sent_to_physician = True
        entry.save()
        return Response({'status': 'sent to physician'})

class PhysicianInfoViewSet(viewsets.ModelViewSet):
    serializer_class = PhysicianInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PhysicianInfo.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Ensure user only has one physician info record
        PhysicianInfo.objects.filter(user=self.request.user).delete()
        serializer.save(user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Data analysis view
class DataAnalysisView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def pain_trends(self, request):
        # Get date range from query params or default to last 30 days
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        entries = PhysicalPainEntry.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        # Prepare data for frontend visualization
        data = {
            'labels': [],
            'datasets': [{
                'label': 'Pain Level',
                'data': []
            }]
        }
        
        for entry in entries:
            data['labels'].append(entry.timestamp.strftime('%Y-%m-%d'))
            data['datasets'][0]['data'].append(entry.pain_level)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def mental_wellness_trends(self, request):
        # Get date range from query params or default to last 30 days
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        entries = MentalWellnessEntry.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        # Prepare data for frontend visualization
        data = {
            'labels': [],
            'datasets': [{
                'label': 'Mental Wellness',
                'data': []
            }]
        }
        
        for entry in entries:
            data['labels'].append(entry.timestamp.strftime('%Y-%m-%d'))
            data['datasets'][0]['data'].append(entry.wellness_level)
        
        return Response(data)
    
class HomeScreenDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = timezone.now()
        
        # Get today's data
        today_pain = PhysicalPainEntry.objects.filter(
            user=user, 
            timestamp__date=today.date()
        ).order_by('-timestamp').first()
        
        today_mental = MentalWellnessEntry.objects.filter(
            user=user, 
            timestamp__date=today.date()
        ).order_by('-timestamp').first()
        
        # Format date for display
        formatted_date = today.strftime('%A, %B %d')
        
        # Get user's first name for the welcome message
        first_name = user.first_name or user.username
        
        # Compile the data
        data = {
            'date': formatted_date,
            'user_name': first_name,
            'has_logged_today': {
                'physical': bool(today_pain),
                'mental': bool(today_mental),
            },
            'latest_entries': {
                'physical': PhysicalPainEntrySerializer(today_pain).data if today_pain else None,
                'mental': MentalWellnessEntrySerializer(today_mental).data if today_mental else None,
            }
        }
        
        return Response(data)