# Generated by Django 4.2.7 on 2024-05-22 14:39

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nombre', models.CharField(max_length=254)),
                ('correo', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=250, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('rol', models.IntegerField(choices=[(1, 'Administrador'), (2, 'Anfitrion'), (3, 'Cliente'), (4, 'Moderador')], default=3)),
                ('foto', models.ImageField(default='planning_travel/media/batman.png', upload_to='planning_travel/media/')),
                ('token_recuperar', models.CharField(blank=True, default='', max_length=254, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=254)),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Comodidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Habitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_habitacion', models.IntegerField()),
                ('ocupado', models.BooleanField()),
                ('capacidad_huesped', models.IntegerField()),
                ('tipo_habitacion', models.CharField(max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=250)),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('direccion', models.CharField(max_length=200)),
                ('cantidad_habitaciones', models.IntegerField()),
                ('dueño', models.CharField(max_length=200)),
                ('ciudad', models.CharField(max_length=200)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=250)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.CharField(max_length=255)),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_llegada', models.DateField()),
                ('fecha_salida', models.DateField()),
                ('cantidad_personas', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=250)),
                ('habitacion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.habitacion')),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=254)),
                ('icono', models.FileField(upload_to='planning_travel/svg_services/')),
            ],
        ),
        migrations.CreateModel(
            name='ReservaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_reserva', models.IntegerField(choices=[(1, 'reservada'), (2, 'libre'), (3, 'cancelada')], default=1)),
                ('fecha_realizacion', models.DateTimeField(auto_now_add=True)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.reserva')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReporteModerador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateField()),
                ('id_reporte', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.reporte')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PisosHotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_piso', models.IntegerField()),
                ('cantidad_habitaciones', models.IntegerField()),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
            ],
        ),
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('numero_contacto', models.CharField(max_length=15)),
                ('foto_perfil', models.CharField(max_length=255)),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField(max_length=300)),
                ('puntuacion', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='La puntuación debe ser como mínimo 1.'), django.core.validators.MaxValueValidator(5, message='La puntuación debe ser como máximo 5.')])),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MetodoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_pago', models.IntegerField(choices=[(1, 'Tarjeta de credito'), (2, 'Tarjeta debito'), (3, 'Efectivo')])),
                ('numero_tarjeta', models.CharField(blank=True, max_length=30, null=True)),
                ('caducidad', models.CharField(blank=True, max_length=6, null=True)),
                ('codigo_cvv', models.CharField(blank=True, max_length=5, null=True)),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HotelServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
                ('id_servicio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.servicio')),
            ],
        ),
        migrations.CreateModel(
            name='HotelComodidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(default=1)),
                ('id_comodidad', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.comodidad')),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
            ],
        ),
        migrations.CreateModel(
            name='HotelCategoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_categoria', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.categoria')),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
            ],
        ),
        migrations.AddField(
            model_name='habitacion',
            name='id_piso_hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.pisoshotel'),
        ),
        migrations.CreateModel(
            name='Foto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_foto', models.ImageField(upload_to='planning_travel/media/')),
                ('descripcion', models.CharField(max_length=255)),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
            ],
        ),
        migrations.CreateModel(
            name='Favorito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_agregado', models.DateField()),
                ('id_hotel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='planning_travel.hotel')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('numero_contacto', models.CharField(max_length=15)),
                ('foto_perfil', models.ImageField(upload_to='planning_travel/media/')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
