# Generated by Django 5.1.6 on 2025-03-08 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='expiration_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
