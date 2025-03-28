# Generated by Django 5.1.6 on 2025-03-22 15:32

import core.storage
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_guia_code_file_alter_guia_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialCarouselImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(storage=core.storage.GridFSStorage(), upload_to='tutorial_carousel/', verbose_name='Imagen del Carrusel')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('tutorial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carousel_images', to='core.tutorial', verbose_name='Tutorial')),
            ],
        ),
    ]
