# Generated by Django 5.1.6 on 2025-03-02 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
