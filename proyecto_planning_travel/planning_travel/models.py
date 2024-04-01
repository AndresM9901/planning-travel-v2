from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=254)
    descripcion = models.TextField()

    def __str__(self):
        return f'{self.nombre}'

class Rol(models.Model):
    nombre = models.CharField(max_length=254)
    descripcion = models.TextField()
    permisos = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nombre}'

class Producto(models.Model):
    nombre = models.CharField(max_length=254, unique=True)
    precio = models.IntegerField()
    inventario = models.IntegerField()
    fecha_creacion = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.nombre}'
    
class Hotel(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    cantidad_habitaciones = models.IntegerField()
    dueño = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=250, decimal_places=2)

    def __str__(self):
        return f'{self.nombre}'
    
class Comodidad(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=200)

    def __str__(self):
        return f'{self.nombre}'
    
class Usuario(models.Model):
    nombre = models.CharField(max_length=254)
    correo = models.EmailField(max_length=254, unique=True)
    contrasena = models.CharField(max_length=100)
    ROLES = (
        (1, "Administrador"),
        (2, "Despachador"),
        (3, "Cliente"),
    )
    rol = models.IntegerField(choices=ROLES, default=3)
    foto = models.ImageField(upload_to="planning_travel/media/")
    # baneado = models.BooleanField()

    def __str__(self):
        return f'{self.nombre}'
    
class Favorito(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    fecha_agregado = models.DateField()

    def __str__(self):
        return f'{self.id_hotel}'
    
# class Comentario(models.Model):
#     id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
#     id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
#     contenido = models.TextField()
#     fecha = models.DateTimeField()

#     def __str__(self):
#         return f'{self.contenido}'
    
# """Agregar tabla de servicios"""
    
# class Puntuacion(models.Model):
#     id_comentario = models.ForeignKey(Comentario, on_delete=models.DO_NOTHING)
#     valoracion = models.IntegerField()

#     def __str__(self):
#         return f'{self.valoracion}'

class Opinion(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    contenido = models.TextField(max_length=300)
    puntuacion = models.IntegerField(validators=[
            MinValueValidator(1, message="La puntuación debe ser como mínimo 1."),
            MaxValueValidator(5, message="La puntuación debe ser como máximo 5."),
        ])
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id_hotel}'
    
class Foto(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    url_foto = models.ImageField(upload_to="planning_travel/media/")
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.id_hotel}'
    
class HotelComodidad(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_comodidad = models.ForeignKey(Comodidad, on_delete=models.DO_NOTHING)
    dispone = models.BooleanField()

    def __str__(self):
        return f'{self.id_hotel}'
    
class Servicio(models.Model):
    nombre = models.CharField(max_length=254)
    icono = models.FileField(upload_to='planning_travel/svg_services/')
    
    def __str__(self):
        return f'{self.nombre}'

class HotelCategoria(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.id_hotel}'

class HotelServicio(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_servicio = models.ForeignKey(Servicio, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.id_hotel}'
    
class Habitacion(models.Model):
    num_habitacion = models.IntegerField()
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    ocupado = models.BooleanField()
    capacidad_huesped = models.IntegerField()
    tipo_habitacion = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.num_habitacion}'

class Reserva(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.DO_NOTHING)
    fecha_llegada = models.DateField()
    fecha_salida = models.DateField()
    cantidad_personas = models.IntegerField()

    def __str__(self):
        return f'{self.habitacion}'

class ReservaUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    reserva = models.ForeignKey(Reserva, on_delete=models.DO_NOTHING)
    estado_reserva = models.CharField(max_length=255)
    fecha_realizacion = models.DateTimeField()

    def __str__(self):
        return f'{self.fecha_realizacion}'

class PerfilUsuario(models.Model):
    id_hotel = models.ForeignKey(Hotel, on_delete=models.DO_NOTHING)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=255)
    numero_contacto = models.CharField(max_length=15)
    foto_perfil = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.id_hotel}'

class Cliente(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=255)
    numero_contacto = models.CharField(max_length=15)
    foto_perfil = models.ImageField(upload_to="planning_travel/media/")

    def __str__(self):
        return f'{self.nombre}'

class Reporte(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.id_usuario}'

class ReporteModerador(models.Model):
    id_reporte = models.ForeignKey(Reporte, on_delete=models.DO_NOTHING)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateField()

    def __str__(self):
        return f'{self.id_reporte}'
