from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.models import User
from .models import UserProfile, UserSettings
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer, UserSettingsSerializer, ChangePasswordSerializer

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