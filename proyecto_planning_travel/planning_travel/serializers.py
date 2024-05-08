from rest_framework import serializers
from .models import *

class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class HotelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id','nombre','descripcion','direccion','categoria','cantidad_habitaciones']

class ComodidadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comodidad
        fields = ['id', 'nombre']

class UsuarioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta: 
        model = Usuario
        fields = ['id', 'nombre','correo','password','rol','foto']

class FavoritoSeralizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Favorito
        fields = ['id', 'id_hotel', 'id_usuario', 'fecha_agregado']

class OpinionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Opinion
        fields = ['id', 'id_hotel', 'id_usuario', 'contenido', 'puntuacion', 'fecha']
# class ComentarioSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Comentario
#         fields = ['id', 'id_hotel', 'id_usuario', 'contenido', 'fecha']

# class PuntuacionSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Puntuacion
#         fields = ['id', 'id_comentario', 'valoracion']

class FotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Foto
        fields = ['id', 'id_hotel', 'url_foto', 'descripcion']

class HotelComodidadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotelComodidad
        fields = ['id', 'id_hotel', 'id_comodidad']

class HotelCategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HotelCategoria
        fields = ['id', 'id_hotel', 'id_categoria']

class HabitacionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Habitacion
        fields = ['id', 'num_habitacion', 'id_hotel','ocupado', 'capacidad_huesped', 'tipo_habitacion']

class ReservaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reserva
        fields = ['id','habitacion', 'fecha_llegada','fecha_salida','cantidad_personas']

class ReservaUsuarioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReservaUsuario
        fields = ['id', 'usuario', 'reserva', 'estado_reserva', 'fecha_realizacion']

class PerfilUsuarioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['id', 'id_hotel', 'id_usuario', 'nombre', 'numero_contacto', 'foto_perfil']

class ClienteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'id_usuario', 'nombre', 'numero_contacto', 'foto_perfil']

class ReporteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reporte
        fields = ['id', 'id_usuario', 'nombre', 'descripcion']

class ReporteModeradorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReporteModerador
        fields = ['id', 'id_reporte', 'id_usuario', 'fecha_inicio', 'fecha_fin']