# Generated by Django 4.2.16 on 2024-09-30 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_favoriterestaurant"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="avatar",
        ),
        migrations.AddField(
            model_name="profile",
            name="birth_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="location",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="profile",
            name="bio",
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
