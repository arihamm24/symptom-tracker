from django.contrib import admin
from .models import (
    UserProfile, UserSettings, PhysicalPainEntry, 
    MentalWellnessEntry, DiaryEntry, PhysicianInfo, Notification
)

admin.site.register(UserProfile)
admin.site.register(UserSettings)
admin.site.register(PhysicalPainEntry)
admin.site.register(MentalWellnessEntry)
admin.site.register(DiaryEntry)
admin.site.register(PhysicianInfo)
admin.site.register(Notification)
