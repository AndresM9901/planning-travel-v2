# Generated by Django 4.2.7 on 2024-09-09 15:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planning_travel', '0004_alter_mensaje_id_destinatario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensaje',
            name='fecha_envio',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
