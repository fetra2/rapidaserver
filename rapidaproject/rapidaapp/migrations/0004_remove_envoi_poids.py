# Generated by Django 4.0.4 on 2022-10-24 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapidaapp', '0003_envoi_poids'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='envoi',
            name='poids',
        ),
    ]
