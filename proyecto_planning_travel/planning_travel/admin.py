from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['id','id_usuario', 'nombre', 'descripcion'] 

@admin.register(ReporteModerador)
class ReporteModeradorAdmin(admin.ModelAdmin):
    list_display = ['id_reporte', 'id_usuario', 'fecha_inicio', 'fecha_fin']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_hotel', 'id_usuario', 'nombre', 'numero_contacto']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'precio', 'inventario', 'fecha_creacion', 'categoria']
    search_fields = ['nombre']
    list_filter = ['categoria', 'fecha_creacion']
    list_editable = ['nombre', 'precio', 'inventario']

class HotelAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'direccion', 'capacidad_huesped', 'precio']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'nombre_en_plural', 'correo', 'password', 'rol','foto']

    def nombre_en_plural(self, obj):
        return mark_safe(
            f'<span style="color: #FFC107;">{obj.nombre}s</span>'
        )


admin.site.register(Cliente)
admin.site.register(Opinion)
admin.site.register(Servicio)
admin.site.register(HotelServicio)
# admin.site.register(Comentario)
admin.site.register(Comodidad)
admin.site.register(Favorito)
admin.site.register(Foto)
admin.site.register(Habitacion)
admin.site.register(Hotel)
admin.site.register(HotelCategoria)
admin.site.register(HotelComodidad)
# admin.site.register(Puntuacion)
admin.site.register(Reserva)
admin.site.register(ReservaUsuario)
admin.site.register(Rol)
