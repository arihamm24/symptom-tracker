# symptomtracker/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    PhysicalPainEntry, MentalWellnessEntry, DiaryEntry, 
    PhysicianInfo, Notification, UserProfile, UserSettings
)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 
            'phone_number', 
            'notification_preference', 
            'medications', 
            'chronic_illnesses', 
            'emergency_contact_name', 
            'emergency_contact_phone',
            'emergency_contact_relationship'
        ]

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'dark_mode', 
            'language', 
            'notification_enabled',
            'reminder_frequency', 
            'health_app_sync',
            'health_app_type',
            'community_enabled',
            'community_username',
            'data_sharing'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    settings = UserSettingsSerializer(required=False, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'settings']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    date_of_birth = serializers.DateField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'date_of_birth']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        date_of_birth = validated_data.pop('date_of_birth')
        
        validated_data.pop('password2')

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        user.profile.date_of_birth = date_of_birth
        user.profile.save()
        
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs
    
class PhysicalPainEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalPainEntry
        fields = ['id', 'pain_level', 'notes', 'timestamp', 'sent_to_physician']
        read_only_fields = ['id', 'timestamp']

class MentalWellnessEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MentalWellnessEntry
        fields = ['id', 'wellness_level', 'notes', 'timestamp', 'sent_to_physician']
        read_only_fields = ['id', 'timestamp']

class DiaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryEntry
        fields = ['id', 'content', 'timestamp', 'sent_to_physician']
        read_only_fields = ['id', 'timestamp']

class PhysicianInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicianInfo
        fields = ['id', 'physician_name', 'physician_email', 'physician_phone']
        read_only_fields = ['id']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'time', 'is_active', 'days']
        read_only_fields = ['id']