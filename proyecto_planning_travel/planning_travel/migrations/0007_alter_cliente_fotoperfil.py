# Generated by Django 4.2.7 on 2023-11-22 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning_travel', '0006_alter_hotel_cantidad_habitaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='fotoPerfil',
            field=models.CharField(max_length=255),
        ),
    ]
