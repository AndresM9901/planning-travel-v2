# Generated by Django 4.2.7 on 2024-07-19 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning_travel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='habitacion',
            name='id_piso_hotel',
        ),
    ]
