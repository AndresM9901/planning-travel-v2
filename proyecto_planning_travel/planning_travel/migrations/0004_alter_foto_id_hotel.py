# Generated by Django 4.2.7 on 2024-10-14 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning_travel', '0003_alter_opinion_id_hotel_alter_opinion_id_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foto',
            name='id_hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning_travel.hotel'),
        ),
    ]
