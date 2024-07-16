from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as views_rest

router = DefaultRouter()
router.register(r'categoria', views.CategoriaViewSet)
router.register(r'hotel', views.HotelViewSet)
router.register(r'comodidad', views.ComodidadViewSet)
router.register(r'usuario', views.UsuarioViewSet)
router.register(r'favorito', views.FavoritoViewSet)
router.register(r'opinion', views.OpinionViewSet)
router.register(r'foto', views.FotoViewSet)
router.register(r'hotel-comodidad', views.HotelComodidadViewSet)
router.register(r'hotel-categoria', views.HotelCategoriaViewSet)
router.register(r'habitacion', views.HabitacionViewSet)
router.register(r'reserva', views.ReservaViewSet)
router.register(r'reserva-usuario', views.ReservaUsuarioViewSet)
router.register(r'perfil-usuario', views.PerfilUsuarioViewSet)
router.register(r'cliente', views.ClienteViewSet)
router.register(r'reporte', views.ReporteViewSet)
router.register(r'reporte-moderador', views.ReporteModeradorViewSet)

urlpatterns = [
    path('inicio/', views.inicio, name="inicio"),
    path('api/1.0/', include(router.urls)),
    path('api/1.0/token-auth/', views_rest.obtain_auth_token),
    path('detalle_hotel/<int:id>/', views.detalle_hotel, name="detalle_hotel"),
    path('admin/', views.index, name="admin"),

    # Reservas
    path('reserva/<int:id>/', views.reserva, name="reserva"),
    path('verificar_disponibilidad/', views.verificar_disponibilidad, name="verificar_disponibilidad"),
    path('separar_reserva/', views.separar_reserva, name="separar_reserva"),
    path('obtener_precio/', views.obtener_precio, name="obtener_precio"),
    path('api/1.0/crear_reserva/', views.CrearReservaAPIView.as_view(), name='crear_reserva'),
    path('api/1.0/verificar_disponibilidad/', views.VerificarDisponibilidadAPIView.as_view(), name='verificar_disponibilidad'),
    
    # Login
    path('login/', views.login, name="login"),
    path('login_form/', views.login_form, name="login_form"),
    path('logout/', views.logout, name="logout"),
    path('registrar/', views.registrar, name="registrar"),
    path('perfil_actualizar/', views.perfil_actualizar, name="perfil_actualizar"),
    path("ver_perfil/", views.ver_perfil, name="ver_perfil"),
    path("recuperar_clave/", views.recuperar_clave, name="recuperar_clave"),
	path("verificar_recuperar/", views.verificar_recuperar, name="verificar_recuperar"),
    
    # Crud de Categorias
    path('categorias_listar/', views.categorias, name="categorias_listar"),
    path('categorias_form/', views.categorias_form, name="categorias_form"),
    path('categorias_crear/', views.categorias_crear, name="categorias_crear"),
    path('categorias_actualizar/', views.categorias_actualizar, name="categorias_actualizar"),
    path('categorias_eliminar/<int:id>/', views.categorias_eliminar, name="categorias_eliminar"),
    path('categorias_formulario_editar/<int:id>/', views.categorias_formulario_editar, name="categorias_formulario_editar"),
    
    # Crud de Usuarios
    path('usuarios_listar/', views.usuarios, name='usuarios_listar'),
    path('usuarios_form/', views.usuarios_form, name='usuarios_form'),
    path('usuarios_crear/', views.usuarios_crear, name='usuarios_crear'),
    path('usuarios_actualizar/', views.usuarios_actualizar, name='usuarios_actualizar'),
    path('usuarios_eliminar/<int:id>/', views.usuarios_eliminar, name='usuarios_eliminar'),
    path('usuarios_form_editar/<int:id>/', views.usuarios_form_editar, name='usuarios_form_editar'),
    
    # Crud de hotel
    path('hoteles_listar/', views.hoteles, name='hoteles_listar'),
    path('hoteles_form/', views.hoteles_form, name='hoteles_form'),
    path('hoteles_crear/', views.hoteles_crear, name='hoteles_crear'),
    path('hoteles_actualizar/', views.hoteles_actualizar, name='hoteles_actualizar'),
    path('hoteles_eliminar/<int:id>', views.hoteles_eliminar, name='hoteles_eliminar'),
    path('hoteles_form_editar/<int:id>', views.hoteles_form_editar, name='hoteles_form_editar'),
    
    #dueño hotel
    path('dueno_hotel/', views.dueno_hotel , name='dueno_hotel'), 
    path('dueno_hoy/', views.dueno_hoy, name='dueno_hoy'), 
    path('dueno_calendario/', views.dueno_calendario, name='dueno_calendario'), 
    path('dueno_anuncio/', views.dueno_anuncio, name='dueno_anuncio'), 
    path('dueno_mensaje/', views.dueno_mensaje, name='dueno_mensaje'), 
    path('dueno_info/', views.dueno_info, name='dueno_info'), 
    path('dueno_ingresos/', views.dueno_ingresos, name='dueno_ingresos'), 
    path('dueno_nuevo_anuncio/', views.dueno_nuevo_anuncio, name='dueno_nuevo_anuncio'), 
    path('dueno_reservaciones/', views.dueno_reservaciones, name='dueno_reservaciones'), 


    # # Crud de puntuaciones
    # path('puntuaciones_listar/', views.puntuaciones, name='puntuaciones_listar'),
    # path('puntuaciones_form/', views.puntuaciones_form, name='puntuaciones_form'),
    # path('puntuaciones_crear/', views.puntuaciones_crear, name='puntuaciones_crear'),
    # path('puntuaciones_actualizar/', views.puntuaciones_actualizar, name='puntuaciones_actualizar'),
    # path('puntuaciones_eliminar/<int:id>', views.puntuaciones_eliminar, name='puntuaciones_eliminar'),
    # path('puntuaciones_form_editar/<int:id>', views.puntuaciones_form_editar, name='puntuaciones_form_editar'),
    
    # Crud de Fotos
    path('fotos_listar/', views.fotos, name='fotos_listar'),
    path('fotos_form/', views.fotos_form, name='fotos_form'),
    path('fotos_crear/', views.fotos_crear, name='fotos_crear'),
    path('fotos_actualizar/', views.fotos_actualizar, name='fotos_actualizar'),
    path('fotos_eliminar/<int:id>', views.fotos_eliminar, name='fotos_eliminar'),
    path('fotos_form_editar/<int:id>', views.fotos_form_editar, name='fotos_form_editar'),
    
    # Crud de hotelComodidad
    path('hoteles_comodidades_listar/', views.hoteles_comodidades, name='hoteles_comodidades_listar'),
    path('hoteles_comodidades_form/', views.hoteles_comodidades_form, name='hoteles_comodidades_form'),
    path('hoteles_comodidades_crear/', views.hoteles_comodidades_crear, name='hoteles_comodidades_crear'),
    path('hoteles_comodidades_actualizar/', views.hoteles_comodidades_actualizar, name='hoteles_comodidades_actualizar'),
    path('hoteles_comodidades_eliminar/<int:id>', views.hoteles_comodidades_eliminar, name='hoteles_comodidades_eliminar'),
    path('hoteles_comodidades_form_editar/<int:id>', views.hoteles_comodidades_form_editar, name='hoteles_comodidades_form_editar'),
    
    # Crud de Reservas
    path('reservas_listar/', views.reservas, name='reservas_listar'),
    path('reservas_form/', views.reservas_form, name='reservas_form'),
    path('reservas_crear/', views.reservas_crear, name='reservas_crear'),
    path('reservas_actualizar/', views.reservas_actualizar, name='reservas_actualizar'),
    path('reservas_eliminar/<int:id>', views.reservas_eliminar, name='reservas_eliminar'),
    path('reservas_form_editar/<int:id>', views.reservas_form_editar, name='reservas_form_editar'),

    # Crud de Reportes
    path('reportes_listar/', views.reportes, name="reportes_listar"),
    path('reportes_form/', views.reportes_form, name="reportes_form"),
    path('reportes_crear/', views.reportes_crear, name="reportes_crear"),
    path('reportes_actualizar/', views.reportes_actualizar, name="reportes_actualizar"),
    path('reportes_eliminar/<int:id>', views.reportes_eliminar, name="reportes_eliminar"),
    path('reportes_form_editar/<int:id>/', views.reportes_form_editar, name="reportes_form_editar"),
    
    # Crud de Reportes Moderador
    path('reportes_moderador_listar/', views.reportes_moderador, name="reportes_moderador_listar"),
    path('reportes_moderador_form/', views.reportes_moderador_form, name="reportes_moderador_form"),
    path('reportes_moderador_crear/', views.reportes_moderador_crear, name="reportes_moderador_crear"),
    path('reportes_moderador_actualizar/', views.reportes_moderador_actualizar, name="reportes_moderador_actualizar"),
    path('reportes_moderador_eliminar/<int:id>', views.reportes_moderador_eliminar, name="reportes_moderador_eliminar"),
    path('reportes_moderador_form_editar/<int:id>/', views.reportes_moderador_form_editar, name="reportes_moderador_form_editar"),
    
    # Crud de Clientes
    path('clientes_listar/', views.clientes, name="clientes_listar"),
    path('clientes_form/', views.clientes_form, name="clientes_form"),
    path('clientes_crear/', views.clientes_crear, name="clientes_crear"),
    path('clientes_actualizar/', views.clientes_actualizar, name="clientes_actualizar"),
    path('clientes_eliminar/<int:id>', views.clientes_eliminar, name="clientes_eliminar"),
    path('clientes_form_editar/<int:id>/', views.clientes_form_editar, name="clientes_form_editar"),
    
    # Crud de Perfil Usuarios
    path('perfil_usuarios_listar/', views.perfil_usuarios, name="perfil_usuarios_listar"),
    path('perfil_usuarios_form/', views.perfil_usuarios_form, name="perfil_usuarios_form"),
    path('perfil_usuarios_crear/', views.perfil_usuarios_crear, name="perfil_usuarios_crear"),
    path('perfil_usuarios_actualizar/', views.perfil_usuarios_actualizar, name="perfil_usuarios_actualizar"),
    path('perfil_usuarios_eliminar/<int:id>', views.perfil_usuarios_eliminar, name="perfil_usuarios_eliminar"),
    path('perfil_usuarios_form_editar/<int:id>/', views.perfil_usuarios_form_editar, name="perfil_usuarios_form_editar"),

    # Crud de Comodidades
    path('comodidades_listar/', views.comodidades, name='comodidades_listar'),
    path('comodidades_form/', views.comodidades_form, name='comodidades_form'),
    path('comodidades_crear/', views.comodidades_crear, name='comodidades_crear'),
    path('comodidades_eliminar/<int:id>', views.comodidades_eliminar, name='comodidades_eliminar'),
    path('comodidades_form_editar/<int:id>', views.comodidades_form_editar, name='comodidades_formulario_editar'),
    path('comodidades_actualizar/', views.comodidades_actualizar, name='comodidades_actualizar'),

    # Crud de habitaciones
    path('habitaciones_listar/', views.habitaciones, name="habitaciones_listar"),
    path('habitaciones_form/', views.habitaciones_form, name="habitaciones_form"),
    path('habitaciones_crear/', views.habitaciones_crear, name="habitaciones_crear"),
    path('habitaciones_eliminar/<int:id>', views.habitaciones_eliminar, name="habitaciones_eliminar"),
    path('habitaciones_form_editar/<int:id>', views.habitaciones_form_editar, name='habitaciones_form_editar'),
    path('habitaciones_actualizar/', views.habitaciones_actualizar, name='habitaciones_actualizar'),

    #Crud de ReservaUsuario
    path('reservas_usuarios_listar/', views.reservas_usuarios, name="reservas_usuarios_listar"),
    path('reservas_usuarios_form/', views.reservas_usuarios_form, name="reservas_usuarios_form"),
    path('reservas_usuarios_crear/', views.reservas_usuarios_crear, name="reservas_usuarios_crear"),
    path('reservas_usuarios_eliminar/<int:id>', views.reservas_usuarios_eliminar, name="reservas_usuarios_eliminar"),
    path('reservas_usuarios_form_editar/<int:id>', views.reservas_usuarios_form_editar, name='reservas_usuarios_form_editar'),
    path('reservas_usuarios_actualizar/', views.reservas_usuarios_actualizar, name='reservas_usuarios_actualizar'),

    # Crud de HotelCategoria
    path('hoteles_categorias_listar/', views.hoteles_categorias, name="hoteles_categorias_listar"),
    path('hoteles_categorias_form/', views.hoteles_categorias_form, name="hoteles_categorias_form"),
    path('hoteles_categorias_crear/', views.hoteles_categorias_crear, name="hoteles_categorias_crear"),
    path('hoteles_categorias_eliminar/<int:id>', views.hoteles_categorias_eliminar, name="hoteles_categorias_eliminar"),
    path('hoteles_categorias_form_editar/<int:id>', views.hoteles_categorias_form_editar, name='hoteles_categorias_form_editar'),
    path('hoteles_categorias_actualizar/', views.hoteles_categorias_actualizar, name='hoteles_categorias_actualizar'),
    
    # # Crud de Comentarios
    # path('comentarios_listar/', views.comentarios, name="comentarios_listar"),
    # path('comentarios_form/', views.comentarios_form, name="comentarios_form"),
    # path('comentarios_crear/', views.comentarios_crear, name="comentarios_crear"),
    # path('comentarios_actualizar/', views.comentarios_actualizar, name="comentarios_actualizar"),
    # path('comentarios_eliminar/<int:id>/', views.comentarios_eliminar, name="comentarios_eliminar"),
    # path('comentarios_form_editar/<int:id>/', views.comentarios_form_editar, name="comentarios_form_editar"),
    
    # Crud de Roles

    # path('roles_listar/', views.roles, name="roles_listar"),
    # path('roles_form/', views.roles_form, name="roles_form"),
    # path('roles_crear/', views.roles_crear, name="roles_crear"),
    # path('roles_actualizar/', views.roles_actualizar, name="roles_actualizar"),
    # path('roles_eliminar/<int:id>/', views.roles_eliminar, name="roles_eliminar"),
    # path('roles_formulario_editar/<int:id>/', views.roles_formulario_editar, name="roles_formulario_editar"),

    # Crud de Favoritos
    path('favoritos_listar/', views.favoritos, name="favoritos_listar"),
    path('favoritos_form/', views.favoritos_form, name="favoritos_form"),
    path('favoritos_crear/', views.favoritos_crear, name="favoritos_crear"),
    path('favoritos_actualizar/', views.favoritos_actualizar, name="favoritos_actualizar"),
    path('favoritos_eliminar/<int:id>/', views.favoritos_eliminar, name="favoritos_eliminar"),
    path('favoritos_formulario_editar/<int:id>/', views.favoritos_formulario_editar, name="favoritos_formulario_editar"),
]
"""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import Usuario

for user in Usuario.objects.all():
    Token.objects.get_or_create(user=user)"""
