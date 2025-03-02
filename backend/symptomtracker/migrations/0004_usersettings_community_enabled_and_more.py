# Generated by Django 5.1.6 on 2025-03-02 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("symptomtracker", "0003_userprofile_emergency_contact_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="community_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="community_username",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="health_app_sync",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="health_app_type",
            field=models.CharField(
                choices=[
                    ("apple", "Apple Health"),
                    ("google", "Google Fit"),
                    ("samsung", "Samsung Health"),
                    ("none", "None"),
                ],
                default="none",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="notification_enabled",
            field=models.BooleanField(default=True),
        ),
    ]
