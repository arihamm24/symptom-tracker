from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    notification_preference = models.CharField(
        max_length=10, 
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both'), ('none', 'None')],
        default='email'
    )
    medications = models.TextField(blank=True, null=True, help_text="List of medications the user is currently taking")
    chronic_illnesses = models.TextField(blank=True, null=True, help_text="List of chronic illnesses the user has been diagnosed with")
    
    # Emergency contact fields
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # Community settings
    reddit_username = models.CharField(max_length=100, blank=True, null=True, help_text="Reddit username for r/ChronicIllness")
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# Create UserProfile automatically when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    # Basic settings
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')

    notification_enabled = models.BooleanField(default=True)
    reminder_frequency = models.CharField(
        max_length=10,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('none', 'None')],
        default='daily'
    )
    data_sharing = models.BooleanField(default=False)  # Opt-in for anonymized data sharing

    # Health App Integration
    health_app_sync = models.BooleanField(default=False)
    health_app_type = models.CharField(
        max_length=20,
        choices=[('apple', 'Apple Health'), ('google', 'Google Fit'), ('samsung', 'Samsung Health'), ('none', 'None')],
        default='none'
    )
    
    # Community connection
    community_enabled = models.BooleanField(default=False)
    community_username = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s settings"

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_settings(sender, instance, **kwargs):
    instance.settings.save()

class PhysicalPainEntry(models.Model):
    PAIN_LEVEL_CHOICES = [
        (1, '1-3: Mild pain'),
        (2, '4-6: Moderate pain'),
        (3, '7-8: Severe pain'),
        (4, '9-13: Debilitating pain')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='physical_pain_entries')
    pain_level = models.IntegerField(choices=PAIN_LEVEL_CHOICES)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    sent_to_physician = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s pain entry on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class MentalWellnessEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mental_wellness_entries')
    wellness_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 scale
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    sent_to_physician = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s mental wellness entry on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    sent_to_physician = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s diary entry on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class PhysicianInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='physician_info')
    physician_name = models.CharField(max_length=100)
    physician_email = models.EmailField()
    physician_phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s physician: {self.physician_name}"

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('medication', 'Medication Reminder'),
        ('appointment', 'Appointment Reminder'),
        ('data_entry', 'Data Entry Reminder')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    days = models.CharField(max_length=100, help_text="Comma-separated list of days (e.g., 'Mon,Tue,Wed')")
    
    def __str__(self):
        return f"{self.user.username}'s {self.notification_type} reminder at {self.time}"