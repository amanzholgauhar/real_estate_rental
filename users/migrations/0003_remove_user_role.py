# Generated by Django 4.2.20 on 2025-05-20 19:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="role",
        ),
    ]
