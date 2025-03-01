# Generated by Django 5.1.6 on 2025-02-27 15:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_lector_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('duration', models.CharField(blank=True, max_length=50, null=True, verbose_name='Duración')),
                ('level', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nivel')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado el')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Actualizado el')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorials', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
        ),
        migrations.CreateModel(
            name='TutorialBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_type', models.CharField(choices=[('text', 'Texto'), ('latex', 'LaTeX'), ('code', 'Código')], max_length=10, verbose_name='Tipo de Bloque')),
                ('content', models.TextField(verbose_name='Contenido')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('tutorial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='core.tutorial')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
