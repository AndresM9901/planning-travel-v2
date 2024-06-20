from .crypt import *
from .models import *
from .serializers import *
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import BadHeaderError, EmailMessage
from django.core.serializers import serialize
from django.db.models import Min
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework import status, viewsets, generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import re

# Create your views here.

def inicio(request):
    # Obtener todos los hoteles, fotos y servicios
    hoteles = Hotel.objects.all()
    fotos = Foto.objects.all()
    servicios = Servicio.objects.all().order_by('nombre')
    servicio_activo = None
    
    if 'logueo' in request.session and 'id' in request.session['logueo']:
        id_usuario = request.session['logueo']['id']
        favoritos = Favorito.objects.filter(id_usuario=id_usuario).values_list('id_hotel_id', flat=True)
    else:
        favoritos = []
        

    habitaciones_total = []
    if 'nombre' in request.GET:
        query_nombre = request.GET.get('nombre')
        hoteles = Hotel.objects.filter(nombre__icontains=query_nombre)
    
    # Filtrar hoteles por servicios seleccionados
    if 'servicio' in request.GET:
        servicio_id = request.GET.get('servicio')
        servicio_activo = servicio_id
        hoteles_servicio = HotelServicio.objects.filter(id_servicio=servicio_id)
        ids_hoteles_servicio = hoteles_servicio.values_list('id_hotel', flat=True)
        hoteles = Hotel.objects.filter(id__in=ids_hoteles_servicio)
        # hoteles = [hotel for hotel in hoteles if hotel.id in hoteles_filtrados]
        # Obtener fotos para los hoteles filtrados
        # fotos_por_hotel = {hotel.id: fotos_por_hotel.get(hotel.id, []) for hotel in hoteles}
        
    # Obtener los hoteles con la cantidad de opiniones y el promedio de valoración
    for hotel in hoteles:
        opiniones_count = Opinion.objects.filter(id_hotel=hotel.id).count()
        valoraciones = Opinion.objects.filter(id_hotel=hotel.id).values_list('puntuacion', flat=True)
        promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0

        hotel.opiniones_count = opiniones_count
        hotel.promedio_valoracion = promedio_valoracion
    
    for hotel in hoteles:
        # Consulta para encontrar el precio mínimo de las habitaciones del hotel actual
        precio_minimo = Habitacion.objects.filter(id_piso_hotel__id_hotel=hotel).aggregate(min_price=Min('precio'))['min_price']
    
        # Actualizar el precio mínimo en el objeto del hotel
        hotel.precio_minimo = precio_minimo
    
    # Crear un diccionario para agrupar las fotos por ID de hotel
    fotos_por_hotel = {}
    for foto in fotos:
        if foto.id_hotel not in fotos_por_hotel:
            fotos_por_hotel[foto.id_hotel] = []
        fotos_por_hotel[foto.id_hotel].append(foto)
    
    # Crear una lista de tuplas que contengan cada hotel y sus fotos asociadas
    hoteles_con_fotos = [(hotel, fotos_por_hotel.get(hotel, [])) for hotel in hoteles]
    if servicio_activo:
        servicio_activo = int(servicio_activo)
    # Enviar los datos a la plantilla
    return render(request, 'planning_travel/hoteles/hotel_home/hotel_home.html', {'favoritos':favoritos,'hoteles': hoteles_con_fotos, 'servicios': servicios, 'servicio_activo': servicio_activo})

def detalle_hotel(request, id):
    hotel = Hotel.objects.get(pk=id)
    servicios_hotel = HotelServicio.objects.filter(id_hotel=id)
    hotel_comodidades = HotelComodidad.objects.filter(id_hotel=id)
    opiniones = Opinion.objects.filter(id_hotel=id)
    pisos_hotel = PisosHotel.objects.filter(id_hotel=id)
    comodidades = []
    servicios = []
    estrellas = []
    if 'logueo' in request.session and 'id' in request.session['logueo']:
        id_usuario = request.session['logueo']['id']
        favoritos = Favorito.objects.filter(id_usuario=id_usuario).values_list('id_hotel_id', flat=True)
    else:
        favoritos = []
    habitaciones_total = []
    for servicio in servicios_hotel:
        sq = Servicio.objects.get(id=servicio.id_servicio.id)
        servicios.append(sq)
    for comodidad in hotel_comodidades:
        cq = Comodidad.objects.get(id=comodidad.id_comodidad.id)
        comodidades.append({"cantidad": comodidad.cantidad, "comodidad": cq})

    for opinion in opiniones:
        opinion.puntuacion = range(opinion.puntuacion)
    for piso in pisos_hotel:
        habitaciones = Habitacion.objects.filter(id_piso_hotel=piso.id)
        habitaciones_total.append(habitaciones)
    fotos = Foto.objects.filter(id_hotel=id)
    comodidades.sort(key=lambda x: x["comodidad"].nombre, reverse=True)
    opiniones_count = Opinion.objects.filter(id_hotel=hotel.id).count()
    valoraciones = Opinion.objects.filter(id_hotel=hotel.id).values_list('puntuacion', flat=True)
    promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0

    servicios.sort(key=lambda x: x.nombre)
    hotel.opiniones_count = opiniones_count
    hotel.promedio_valoracion = promedio_valoracion
    contexto = {
        'hotel': hotel,
        'servicios': servicios,
        'habitaciones': habitaciones_total,
        'fotos': fotos,
        'comodidades': comodidades,
        'opiniones': opiniones,
        'favoritos':favoritos,
    }
    return render(request, 'planning_travel/hoteles/hotel_home/hotel_detail.html', contexto)

def reserva(request, id):
    hotel = Hotel.objects.get(pk=id)
    pisos = PisosHotel.objects.filter(id_hotel=id)
    num_habitaciones_piso = []
    habitaciones = []
    logueo = request.session.get("logueo", False)
    if  logueo:
        usuario = Usuario.objects.get(pk=request.session['logueo']['id'])
        metodo_usuario = tuple((m.id, m.get_tipo_pago_display()) for m in MetodoPago.objects.filter(id_usuario=usuario.id))
        if metodo_usuario:
            print(tuple(metodo_usuario))
        else:
            metodo = MetodoPago()
            metodo_usuario = metodo.TIPO_PAGO

    
        for piso in pisos:
            habitacion_hotel = Habitacion.objects.filter(id_piso_hotel=piso.id)
            habitaciones.append(habitacion_hotel)
            num_habitaciones_piso.append({'piso': piso, 'habitaciones': habitacion_hotel})
            
        habitaciones_disponibles = []
        if request.method == 'POST':
            fecha_llegada = request.POST.get('fecha_llegada')
            fecha_salida = request.POST.get('fecha_salida')
            
            response = request.post('verificar_disponibilidad/', data={
                'fecha_llegada': fecha_llegada,
                'fecha_salida': fecha_salida
            })
            
            if response.status.code == 200:
                data = response.json()
                habitaciones_disponibles = data.get('habitaciones_disponibles', [])
        
        contexto = {
            'habitaciones': habitaciones,
            'num_habitaciones_piso': num_habitaciones_piso,
            'habitaciones_disponibles': habitaciones_disponibles,
            'metodo_pago': metodo_usuario
        }
        return render(request, 'planning_travel/hoteles/reservas/reservas.html', contexto)
    else:
        return redirect('login_form')


def verificar_disponibilidad(request):
    fecha_llegada_str = request.POST.get('fecha_llegada')
    fecha_salida_str = request.POST.get('fecha_salida')
    
    if fecha_llegada_str is None or fecha_salida_str is None:
        return JsonResponse({'error': 'Las fechas de llegada y salida son necesarias'}, status=400)
    
    fecha_llegada = datetime.strptime(fecha_llegada_str, '%Y-%m-%d')
    fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d')

    habitaciones_ocupadas = Habitacion.objects.filter(
        reserva__fecha_llegada__lte=fecha_salida,
        reserva__fecha_salida__gte=fecha_llegada
    ).values_list('num_habitacion', flat=True)

    habitaciones_disponibles = Habitacion.objects.exclude(
        reserva__fecha_llegada__lte=fecha_salida,
        reserva__fecha_salida__gte=fecha_llegada
    ).values_list('num_habitacion', flat=True)
    print(f'{fecha_llegada}, {fecha_salida}')
    return JsonResponse({
        'habitaciones_ocupadas': list(habitaciones_ocupadas),
        'habitaciones_disponibles': list(habitaciones_disponibles)
    })
    
def separar_reserva(request):
    if request.method == 'POST':
        habitacion = request.POST.get('habitacion')
        fecha_llegada = request.POST.get('fecha_llegada')
        fecha_salida = request.POST.get('fecha_salida')
        num_huespedes = request.POST.get('num_personas')
        try:
            qh = Habitacion.objects.get(pk=habitacion)
            reserva = Reserva(
                habitacion=qh,
                fecha_llegada=fecha_llegada,
                fecha_salida=fecha_salida,
                cantidad_personas=num_huespedes,
                total=qh.precio
            )
            reserva.save()
            if request.session['logueo']:
                usuario = Usuario.objects.get(pk=request.session['logueo']['id'])
                reserva_usuario = ReservaUsuario(
                    usuario=usuario,
                    reserva=reserva
                )
                reserva_usuario.save()
            else:
                messages.success(request, "Fue reservado correctamente")
                hotel = Hotel.objects.get(pk=PisosHotel.objects.get(pk=Habitacion.objects.get(pk=habitacion.id)))
                url = reverse('reserva', kwargs={'id': hotel.id})
                return redirect(url)
            messages.success(request, "Fue reservado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        hotel = Hotel.objects.get(pk=PisosHotel.objects.get(pk=Habitacion.objects.get(pk=habitacion.id)))
        url = reverse('reserva', kwargs={'id': hotel.id})
        messages.warning(request, 'No se pudo hacer la reserva')
        return redirect(url)
    return redirect('inicio')

def obtener_precio(request):
    habitacion_seleccionada = request.GET.get('habitacion')
    
    precio = 0
    
    if habitacion_seleccionada:
        habitacion = Habitacion.objects.get(pk=habitacion_seleccionada)
        precio = habitacion.precio
        
    return JsonResponse({'precio': precio})

def agregar_pago(request):
    return redirect('ver_perfil')

class CrearReservaAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReservaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerificarDisponibilidadAPIView(APIView):
    def get(self, request):
        fecha_llegada_str = request.GET.get('fecha_llegada')
        fecha_salida_str = request.GET.get('fecha_salida')

        if fecha_llegada_str is None or fecha_salida_str is None:
            return Response({'error': 'Las fechas de llegada y salida son necesarias'}, status=status.HTTP_400_BAD_REQUEST)

        fecha_llegada = datetime.strptime(fecha_llegada_str, '%Y-%m-%d')
        fecha_salida = datetime.strptime(fecha_salida_str, '%Y-%m-%d')

        habitaciones_ocupadas = Habitacion.objects.filter(
            reserva__fecha_llegada__lte=fecha_salida,
            reserva__fecha_salida__gte=fecha_llegada
        ).values_list('id', flat=True)

        habitaciones_disponibles = Habitacion.objects.exclude(
            reserva__fecha_llegada__lte=fecha_salida,
            reserva__fecha_salida__gte=fecha_llegada
        ).values_list('id', flat=True)

        return Response({
            'habitaciones_ocupadas': list(habitaciones_ocupadas),
            'habitaciones_disponibles': list(habitaciones_disponibles)
        })

class InicioHoteles(APIView):
    def get(self, request):
        # Obtener todos los hoteles, fotos y servicios
        hoteles = Hotel.objects.all()
        fotos = Foto.objects.all()
        url = f'http://192.168.56.1:8000'
        
        habitaciones_total = []
        if 'nombre' in request.GET:
            query_nombre = request.GET.get('nombre')
            hoteles = Hotel.objects.filter(nombre__icontains=query_nombre)
        
        if 'servicio' in request.GET:
            servicio_id = request.GET.get('servicio')
            servicio_activo = servicio_id
            hoteles_servicio = HotelServicio.objects.filter(id_servicio=servicio_id)
            ids_hoteles_servicio = hoteles_servicio.values_list('id_hotel', flat=True)
            hoteles = Hotel.objects.filter(id__in=ids_hoteles_servicio)
        
        # Serializar los hoteles
        hoteles_serializados = []
        for hotel in hoteles:
            opiniones_count = Opinion.objects.filter(id_hotel=hotel.id).count()
            valoraciones = Opinion.objects.filter(id_hotel=hotel.id).values_list('puntuacion', flat=True)
            promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0

            hotel_dict = model_to_dict(hotel)
            hotel_dict['opiniones_count'] = opiniones_count
            hotel_dict['promedio_valoracion'] = promedio_valoracion
            
            # Obtener fotos para el hotel actual y agregarlas al diccionario del hotel
            fotos_hotel = fotos.filter(id_hotel=hotel.id)
            fotos_serializadas = [f"{url}{foto.url_foto.url}" for foto in fotos_hotel]
            hotel_dict['fotos'] = fotos_serializadas
            hoteles_serializados.append(hotel_dict)

        
        return Response({'hoteles': hoteles_serializados})

from django.shortcuts import get_object_or_404

class DetalleHotel(APIView):
    def get(self, request, id):
        # Obtener el hotel, devolver un error 404 si no existe
        hotel = get_object_or_404(Hotel, pk=id)

        # Obtener servicios del hotel
        servicios_hotel = HotelServicio.objects.filter(id_hotel=id)
        servicios = [servicio.id_servicio for servicio in servicios_hotel]

        # Obtener comodidades del hotel
        hotel_comodidades = HotelComodidad.objects.filter(id_hotel=id)
        comodidades = [{"cantidad": comodidad.cantidad, "comodidad": comodidad.id_comodidad} for comodidad in hotel_comodidades]

        # Obtener opiniones del hotel
        opiniones = Opinion.objects.filter(id_hotel=id)
        for opinion in opiniones:
            opinion.puntuacion_range = list(range(opinion.puntuacion))  # Crear una lista con la puntuación

        # Obtener habitaciones del hotel por piso
        pisos_hotel = PisosHotel.objects.filter(id_hotel=id)
        habitaciones_total = [Habitacion.objects.filter(id_piso_hotel=piso.id) for piso in pisos_hotel]

        # Obtener fotos del hotel
        fotos = Foto.objects.filter(id_hotel=id)

        # Calcular la cantidad de opiniones y la valoración promedio
        opiniones_count = opiniones.count()
        valoraciones = opiniones.values_list('puntuacion', flat=True)
        promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0
        
        precio_minimo = Habitacion.objects.filter(id_piso_hotel__id_hotel=hotel).aggregate(min_price=Min('precio'))['min_price']

        # Ordenar comodidades y servicios
        comodidades.sort(key=lambda x: x["comodidad"].nombre, reverse=True)
        servicios.sort(key=lambda x: x.nombre)

        # Crear el contexto de la respuesta
        contexto = {
            'hotel': {
                'id': hotel.id,
                'nombre': hotel.nombre,
                'direccion': hotel.direccion,
                'ciudad': hotel.ciudad,
                'precio': precio_minimo,
                'promedio': promedio_valoracion,
                'num_opiniones': opiniones_count
            },
            'servicios': [{'id': servicio.id, 'nombre': servicio.nombre} for servicio in servicios],
            'habitaciones': [[{'id': habitacion.id, 'nombre': habitacion.num_habitacion} for habitacion in habitaciones] for habitaciones in habitaciones_total],
            'fotos': [{'id': foto.id, 'url': foto.url_foto.url} for foto in fotos],
            'comodidades': [{'cantidad': comodidad['cantidad'], 'nombre': comodidad['comodidad'].nombre} for comodidad in comodidades],
            'opiniones': [{'id': opinion.id, 'puntuacion': opinion.puntuacion, 'comentario': opinion.contenido, 'usuario': opinion.id_usuario.nombre} for opinion in opiniones]
        }

        return Response(contexto, status=status.HTTP_200_OK)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


class CustomAuthToken(ObtainAuthToken):
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['username']
		# traer datos del usuario para bienvenida y ROL
		usuario = Usuario.objects.get(nick=user)
		token, created = Token.objects.get_or_create(user=usuario)

		return Response({
			'token': token.key,
			'user': {
				'user_id': usuario.pk,
				'email': usuario.email,
				'nombre': usuario.nombre,
				'apellido': usuario.apellido,
				'rol': usuario.rol,
				'foto': usuario.foto.url
			}
		})


class HacerReserva(APIView):
    def post(self, request):
        print(request.data)
        if request.method == 'POST':
            id_usuario = request.data['idUsuario']
            habitacion = request.data['habitacion']
            fecha_llegada = request.data['fechaLlegada']
            fecha_salida = request.data['fechaSalida']
            num_huespedes = request.data['numHuespedes']
            try:
                qh = Habitacion.objects.get(pk=habitacion)
                reserva = Reserva(
                    habitacion=qh,
                    fecha_llegada=fecha_llegada,
                    fecha_salida=fecha_salida,
                    cantidad_personas=num_huespedes,
                    total=qh.precio
                )
                reserva.save()
                if get_object_or_404(Usuario, pk=id_usuario):
                    usuario = Usuario.objects.get(pk=id_usuario)
                    reserva_usuario = ReservaUsuario(
                        usuario=usuario,
                        reserva=reserva
                    )
                    reserva_usuario.save()
                    print(f'reserva hecha')
                else:
                    print('no se hizo reserva')
                    return Response(status=404)
            except Exception as e:
                print(f'no se hizo reserva2 {e}')
                return Response(status=404)
        else:
            return Response(status=404)
        return Response(data={'message': 'Reserva creada correctamente'}, status=201)
    
class RegistrarUsuario(APIView):
    def post(self, request):
        print(request.data)
        if request.method == "POST":
            nombre = request.data["nombre"]
            apellido = request.data["apellido"]
            correo = request.data["correo"]
            clave = request.data["password"]
            confirmar_clave = request.data["confirmPassword"]
            nick = correo.split('@')[0]
            if nombre == "" or correo == "" or clave == "" or confirmar_clave == "":
                return Response(data={'message': 'Todos los campos son obligatorios', 'respuesta': 400}, status=400)
            elif not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
                return Response(data={'message': 'El correo no es válido', 'respuesta': 400}, status=400)
            elif clave != confirmar_clave:
                return Response(data={'message': 'Las contraseñas no coinciden', 'respuesta': 400}, status=400)
            else:
                try:
                    q = Usuario(
                        nombre=nombre,
                        apellido=apellido,
                        email=correo,
                        password=make_password(clave),
                        nick=nick
                    )
                    q.save()
                except Exception as e:
                    return Response(data={'message': 'El Usuario ya existe', 'respuesta': 409}, status=409)

        # Renderiza la misma página de registro con los mensajes de error
        return Response(data={'message': f'Usuario creado correctamente tu nick es: {nick}', 'respuesta': 201}, status=201)

class VerReservaUsuario(APIView):
    def get(self, request, id):
        usuarioQ = get_object_or_404(Usuario, pk=id)
        reservaUsuarioQ = ReservaUsuario.objects.filter(usuario=usuarioQ.id)
        reservas = []
        for reserva in reservaUsuarioQ:
            reservas.append({
                'reserva': {
                    'id': reserva.reserva.id,
                    'habitacion': reserva.reserva.habitacion.num_habitacion,
                    'fecha_llegada': reserva.reserva.fecha_llegada,
                    'fecha_salida': reserva.reserva.fecha_salida,
                    'num_huespedes': reserva.reserva.cantidad_personas,
                    'precio': reserva.reserva.total
                    },
                'estado_reserva': reserva.estado_reserva,
                'fecha_realizacion': reserva.fecha_realizacion
                })
        contexto = {
            'usuario': usuarioQ.nombre,
            'reservas': reservas
        }
        return Response(contexto)
    
def terminos_condiciones(request):
    return render(request, 'planning_travel/terminos/terminos.html')

class DeleteUserView(generics.DestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            # Obtiene el usuario que se va a eliminar
            user = self.get_object()
            
            # Obtiene el usuario autenticado
            authenticated_user = request.user
            
            # Comprueba si el usuario autenticado es el mismo que el usuario a eliminar
            if authenticated_user != user:
                return Response({'error': 'No tienes permisos para eliminar este usuario'}, status=status.HTTP_403_FORBIDDEN)
            
            # Elimina el usuario
            user.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Usuario.DoesNotExist:
            return Response({'error': 'El usuario especificado no existe'}, status=status.HTTP_404_NOT_FOUND)

# Crud de Categorias
def categorias(request):
    # select * from categorias
    consulta = Categoria.objects.all()
    context = {'data': consulta}
    return render(request, 'planning_travel/categorias/categorias.html', context)

def categorias_form(request):
    return render(request, 'planning_travel/categorias/categorias_form.html')

def categorias_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Categoria(
                nombre=nombre,
                descripcion=descripcion
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('categorias_listar')
    else:
        messages.warning(request, 'No se enviaron datos')
        return redirect('categorias_listar')

def categorias_eliminar(request, id):
    try:
        q = Categoria.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Categoria eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('categorias_listar')

def categorias_formulario_editar(request, id):

    q = Categoria.objects.get(pk = id)
    contexto = {'data': q}

    return render(request, 'planning_travel/categorias/categorias_form_editar.html', contexto)

def categorias_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Categoria.objects.get(pk = id)
            q.nombre = nombre
            q.descripcion = descripcion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('categorias_listar')

regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
def login_form(request):
    return render(request, 'planning_travel/login/login.html')

def login(request):
    if request.method == "POST":
        user = request.POST.get("correo")
        password = request.POST.get("clave")
        # select * from Usuario where correo = "user" and clave = "passw"
        if user == "" or password == "":
            messages.error(request, "No se permiten campos vacios")
        else:
            if not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user):
                messages.error(request, "El correo no es válido")
            else:
                try:
                    q = Usuario.objects.get(email=user)
                    if verify_password(password, q.password):
                        # Crear variable de sesión
                        request.session["logueo"] = {
                            "id": q.id,
                            "nombre": q.nombre,
                            "rol": q.rol,
                            "nombre_rol": q.get_rol_display()
                        }
                        request.session["carrito"] = []
                        request.session["items"] = 0
                        messages.success(request, f"Bienvenido {q.nombre}!!")
                        return redirect("inicio")
                    else:
                        messages.error(request, f"Usuario o contraseña incorrecto")
                        return redirect("login_form")
                except Exception as e:
                    print(f'{user}, {password}')
                    messages.error(request, "Error: Usuario o contraseña incorrectos...")

    else:
        return redirect("login_form")  # Redirige solo en caso de GET
    # Renderiza la misma página de inicio de sesión con los mensajes de error
    return render(request, "planning_travel/login/login.html")

def registrar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo")
        clave = request.POST.get("clave")
        confirmar_clave = request.POST.get("confirmar_clave")
        nick = correo.split('@')[0]
        if nombre == "" or correo == "" or clave == "" or confirmar_clave == "":
            messages.error(request, "Todos los campos son obligatorios")
        elif not re.match(r'^[a-zA-Z ]+$', nombre):
            messages.error(request, "El nombre solo puede contener letras y espacios")
        elif not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            messages.error(request, "El correo no es válido")
        elif clave != confirmar_clave:
            messages.error(request, "Las contraseñas no coinciden")
        else:
            try:
                q = Usuario(
                    nombre=nombre,
                    apellido=apellido,
                    email=correo,
                    password=make_password(clave),
                    nick=nick
                )
                q.save()
                messages.success(request, "Usuario registrado exitosamente")
            except Exception as e:
                messages.error(request, f"El Usuario ya existe {e}")

    # Renderiza la misma página de registro con los mensajes de error
    return render(request, "planning_travel/login/login.html")

def logout(request):
	try:
		del request.session["logueo"]
		messages.success(request, "Sesión cerrada correctamente!")
		return redirect("inicio")
	except Exception as e:
		messages.warning(request, "No se pudo cerrar sesión...")
		return redirect("inicio")

def recuperar_clave(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        if correo == "":
            messages.error(request, "Todos los campos son obligatorios")
            return redirect("login_form")
        else:
            try:
                q = Usuario.objects.get(email=correo)
                from random import randint
                import base64
                token = base64.b64encode(str(randint(100000, 999999)).encode("ascii")).decode("ascii")
                print(token)
                q.token_recuperar = token
                q.save()
                # enviar correo de recuperación
                destinatario = correo
                mensaje = f"""
                        <h1 style='color:#ff5c5c;'>Planning Travel</h1>
                        <p>Usted ha solicitado recuperar su contraseña, haga clic en el link y digite el token.</p>
                        <p>Token: <strong>{token}</strong></p>
                        <p>Click Aquí:</p>
                        <a href='http://127.0.0.1:8000/planning_travel/verificar_recuperar/?correo={correo}'>Recuperar Clave</a>
                        """
                try:
                    msg = EmailMessage("Tienda ADSO", mensaje, settings.EMAIL_HOST_USER, [destinatario])
                    msg.content_subtype = "html"  # Habilitar contenido html
                    msg.send()
                    messages.success(request, "Correo enviado!!")
                except BadHeaderError:
                    messages.error(request, "Encabezado no válido")
                except Exception as e:
                    messages.error(request, f"Error: {e}")
                # fin -
            except Usuario.DoesNotExist:
                messages.error(request, "No existe el usuario....")
            return redirect("recuperar_clave")
    else:
        return render(request, "planning_travel/login/login.html")
from django.urls import reverse

def verificar_recuperar(request):
    if request.method == "POST":
        if request.POST.get("check"):
            # caso en el que el token es correcto
            correo = request.POST.get("correo")
            q = Usuario.objects.get(email=correo)

            c1 = request.POST.get("nueva1")
            c2 = request.POST.get("nueva2")
            if c1 == "" or c2 == "":
                messages.info(request, "Campos vacios")
                return redirect(reverse('verificar_recuperar') + f"?correo={correo}")
            else:
                if c1 == c2:
                    # cambiar clave en DB
                    q.password = make_password(c1)
                    q.token_recuperar = ""
                    q.save()
                    messages.success(request, "Contraseña guardada correctamente!!")
                    return redirect("login_form")
                else:
                    messages.info(request, "Las contraseñas nuevas no coinciden...")
                    return redirect(reverse('verificar_recuperar') + f"?correo={correo}")
        else:
            # caso en el que se hace clic en el correo-e para digitar token
            correo = request.POST.get("correo")
            token = request.POST.get("token")
            q = Usuario.objects.get(email=correo)
            if token == "":
                messages.info(request, "Complete todos los espacios")
                return redirect(reverse('verificar_recuperar') + f"?correo={correo}")
            else:
                if (q.token_recuperar == token) and q.token_recuperar != "":
                    contexto = {"check": "ok", "correo":correo}
                    return render(request, "planning_travel/login/verificar_recuperar.html", contexto)
                else:
                    messages.error(request, "Token incorrecto")
                    return redirect(reverse('verificar_recuperar') + f"?correo={correo}")
    else:
        correo = request.GET.get("correo")
        contexto = {"correo":correo}
        return render(request, "planning_travel/login/verificar_recuperar.html", contexto)
    
def ver_perfil(request):
	logueo = request.session.get("logueo", False)
	# Consultamos en DB por el ID del usuario logueado....
	q = Usuario.objects.get(pk=logueo["id"])
	contexto = {"data": q}
	return render(request, "planning_travel/login/perfil_usuario.html", contexto)

def perfil_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        try:
            # Obtén el objeto Usuario por su ID
            usuario = Usuario.objects.get(pk=id)
            usuario.nombre = nombre
            usuario.correo = correo
            usuario.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('ver_perfil')  # Redirecciona a una página después de la actualización
        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe")
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        messages.warning(request, 'No se enviaron datos')
    return redirect('ver_perfil')  # Redirecciona en caso de un error o método GET

def index(request):
    return render(request, 'planning_travel/inicio.html')

#andres
def reservas_mostrar(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        usuario_id = request.session["logueo"]["id"]
        reservas_usuario = ReservaUsuario.objects.filter(usuario=usuario_id)
        return render(request, 'planning_travel/hoteles/reservas/reservas_mostrar.html', {'reservas_usuario': reservas_usuario})
    else:
        return redirect('login_form')
        
def favoritos_mostrar(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        favoritos_usuario = Favorito.objects.filter(id_usuario=request.session["logueo"]["id"])    
        hoteles_con_fotos = []
        for favorito in favoritos_usuario:
            hotel = favorito.id_hotel
            # Obtener la primera foto de cada hotel
            primera_foto = Foto.objects.filter(id_hotel=hotel).first()
            hoteles_con_fotos.append({'hotel': hotel, 'foto': primera_foto})
        print(hoteles_con_fotos)
        return render(request, 'planning_travel/hoteles/favoritos/favoritos_mostrar.html', {'data': hoteles_con_fotos, 'favorito': favoritos_usuario})
    else:
        return redirect('login_form')
def favoritos_crearUser(request, id_hotel):
    logueo = request.session.get("logueo", False)
    if logueo:
        qh = Hotel.objects.get(pk=id_hotel)
        qu = Usuario.objects.get(pk=request.session["logueo"]["id"])

        if Favorito.objects.filter(id_hotel=qh, id_usuario=qu).exists():
            favorito = Favorito.objects.get(id_hotel=qh, id_usuario=qu)
            favorito.delete()
            messages.warning(request, 'Hotel favorito eliminado correctamente!!')
            return redirect('inicio')
        else:
            favorito = Favorito(
                id_hotel = qh,
                id_usuario = qu,
            )    
            favorito.save()
            messages.success(request, 'Hotel favorito agregado correctamente!!')
            return redirect('inicio')
    else:
        return redirect('login_form')
    
def favoritos_crearUser2(request, id_hotel):
    logueo = request.session.get("logueo", False)
    if logueo:
        qh = Hotel.objects.get(pk=id_hotel)
        qu = Usuario.objects.get(pk=request.session["logueo"]["id"])

        if Favorito.objects.filter(id_hotel=qh, id_usuario=qu).exists():
            favorito = Favorito.objects.get(id_hotel=qh, id_usuario=qu)
            favorito.delete()
            messages.warning(request, 'Hotel favorito eliminado correctamente!!')
            return redirect('favoritos_mostrar')
        else:
            favorito = Favorito(
                id_hotel = qh,
                id_usuario = qu,

            )    
            favorito.save()
            messages.success(request, 'Hotel favorito agregado correctamente!!')
            return redirect('favoritos_mostrar')
    else:
        return redirect('login_form')
def favoritos_crearUser3(request, id_hotel):
    logueo = request.session.get("logueo", False)
    if logueo:
        qh = Hotel.objects.get(pk=id_hotel)
        qu = Usuario.objects.get(pk=request.session["logueo"]["id"])

        if Favorito.objects.filter(id_hotel=qh, id_usuario=qu).exists():
            favorito = Favorito.objects.get(id_hotel=qh, id_usuario=qu)
            favorito.delete()
            messages.warning(request, 'Hotel favorito eliminado correctamente!!')
            return redirect('detalle_hotel', id_hotel)
        else:
            favorito = Favorito(
                id_hotel = qh,
                id_usuario = qu,

            )    
            favorito.save()
            messages.success(request, 'Hotel favorito agregado correctamente!!')
            return redirect('detalle_hotel', id_hotel)
    else:
        return redirect('login_form')  
def registrar_form(request):
    return render(request, 'planning_travel/login/registrar.html')

# Crud de Usuarios
def usuarios(request):
    q = Usuario.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/login/usuarios.html', contexto)

def usuarios_form(request):
    return render(request, 'planning_travel/login/usuarios_form.html')

def usuarios_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        rol = Usuario.objects.get(pk=request.POST.get("rol"))
        foto = request.FILES.get('foto')
        try:
            q = Usuario(
                nombre=nombre,
                correo=correo,
                contrasena=contrasena,
                rol=rol,
                foto=foto,
            )
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('usuarios_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('usuarios_listar')
    
def usuarios_eliminar(request, id):
    try:
        q = Usuario.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Usuario eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('usuarios_listar')

def usuarios_form_editar(request, id):
    q = Usuario.objects.get(pk = id)
    contexto = {'data': q}

    return render(request, 'planning_travel/login/usuarios_form_editar.html', contexto)

def usuarios_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        foto = request.POST.get('foto')
        try:
            q = Usuario.objects.get(pk = id)
            q.nombre = nombre
            q.correo = correo
            q.contrasena = contrasena
            q.foto = foto
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')

    return redirect('usuarios_listar')

# Crud de Hoteles

def hoteles(request):
    q = Hotel.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/hoteles/hoteles.html', contexto)

def hoteles_form(request):
    q = Categoria.objects.all()
    d = Usuario.objects.all()
    contexto = {'data': q, 'dueno': d}
    return render(request, 'planning_travel/hoteles/hoteles_form.html', contexto)

def hoteles_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        categoria = Categoria.objects.get(pk=request.POST.get('categoria'))
        propietario = Usuario.objects.get(pk=request.POST.get('propietario'))
        ciudad = request.POST.get('ciudad')
        try:
            q = Hotel(
                nombre=nombre,
                descripcion=descripcion,
                direccion=direccion,
                categoria=categoria,
                propietario=propietario,
                ciudad=ciudad
            )
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('hoteles_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('usuarios_listar')
    
def hoteles_eliminar(request, id):
    try:
        q = Hotel.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Hotel eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('hoteles_listar')

def hoteles_form_editar(request, id):
    q = Hotel.objects.get(pk = id)
    c = Categoria.objects.all()
    contexto = {'data': q, 'categoria': c}

    return render(request, 'planning_travel/hoteles/hoteles_form_editar.html', contexto)

def hoteles_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        categoria = Categoria.objects.get(pk=request.POST.get("categoria"))
        cantidad_habitacion = request.POST.get('cantidad_habitacion')
        try:
            q = Hotel.objects.get(pk = id)
            q.nombre = nombre
            q.descripcion = descripcion
            q.direccion = direccion
            q.categoria = categoria
            q.cantidad_habitacion = cantidad_habitacion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')

# Crud Comodidades

def comodidades(request):
    q = Comodidad.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/comodidades/comodidad.html', contexto)

def comodidades_form(request):
    return render(request, 'planning_travel/comodidades/comodidad_form.html')

def comodidades_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Comodidad(
                nombre=nombre,
                descripcion=descripcion
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('comodidades_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('comodidades_listar')
    
def comodidades_eliminar(request, id):
    try:
        q = Comodidad.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Comodidad eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('comodidades_listar')

def comodidades_form_editar(request, id):
    q = Comodidad.objects.get(pk = id)
    contexto = {'data': q}
    return render(request, 'planning_travel/comodidades/comodidad_form_editar.html', contexto)

def comodidades_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Comodidad.objects.get(pk = id)
            q.nombre = nombre
            q.descripcion = descripcion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('comodidades_listar')

# Crud habitaciones
def habitaciones(request):
    q = Habitacion.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/habitaciones/habitaciones.html', contexto)

def habitaciones_form(request):
    q = Hotel.objects.all()
    c = Foto.objects.all()
    contexto = {'data': q, 'foto': c}
    
    return render(request, 'planning_travel/habitaciones/habitaciones_form.html', contexto)

def habitaciones_crear(request):
    if request.method == 'POST':
        num_habitacion = request.POST.get('num_habitacion')
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        ocupado = request.POST.get('ocupado')
        ocupado = True if ocupado == 'on' else False    
        capacidad_huesped = request.POST.get('capacidad_huesped')
        tipo_habitacion = request.POST.get('tipoHabitacion')
        try:
            q = Habitacion(
                num_habitacion = num_habitacion,
                id_hotel = hotel,
                ocupado = ocupado,
                capacidad_huesped = capacidad_huesped,
                tipo_habitacion = tipo_habitacion,
            )
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('habitaciones_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('habitaciones_listar')

def habitaciones_eliminar(request, id):
    try:
        q = Habitacion.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Habitación eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')
    
    return redirect("habitaciones_listar")

def habitaciones_form_editar(request, id):
    c = Foto.objects.all()
    q = Hotel.objects.all()
    r = Habitacion.objects.get(pk = id)
    contexto = {'data': q, 'foto' : c, 'habitacion': r }
    return render(request, 'planning_travel/habitaciones/habitaciones_form_editar.html', contexto)

def habitaciones_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        num_habitacion = request.POST.get('num_habitacion')
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        ocupado = request.POST.get('ocupado')
        ocupado = True if ocupado == 'on' else False    
        capacidad_huesped = request.POST.get('capacidad_huesped')
        tipo_habitacion = request.POST.get('tipoHabitacion')
        try:
            q = Habitacion.objects.get(pk = id)
            q.num_habitacion = num_habitacion
            q.id_hotel = hotel
            q.ocupado = ocupado
            q.capacidad_huesped = capacidad_huesped
            q.tipo_habitacion = tipo_habitacion
            q.save()
            messages.success(request, "Fue actualizado correctamente")

        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('habitaciones_listar')

# Crud ReservaUsuarios
def reservas_usuarios(request):
    q = ReservaUsuario.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/reservas_usuarios/reservas_usuarios.html', contexto)

def reservas_usuarios_form(request):
    q = Usuario.objects.all()
    c = Reserva.objects.all()
    contexto = {'data': q, 'reserva': c}
    
    return render(request, 'planning_travel/reservas_usuarios/reservas_usuarios_form.html', contexto)

def reservas_usuarios_crear(request):
    if request.method == 'POST':
        
        usuario = Usuario.objects.get(pk=request.POST.get('usuario'))
        reserva = Reserva.objects.get(pk=request.POST.get('reserva'))
        estado_reserva = request.POST.get('estado_reserva')
        fecha_realizacion = request.POST.get('fecha_realizacion')
        try:
            q = ReservaUsuario(
                usuario = usuario,
                reserva = reserva,
                estado_reserva = estado_reserva,
                fecha_realizacion = fecha_realizacion
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('reservas_usuarios_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('reservas_usuarios_listar')

def reservas_usuarios_eliminar(request, id):
    try:
        q = ReservaUsuario.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Habitación eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')
    
    return redirect("reservas_usuarios_listar") 

def reservas_usuarios_form_editar(request, id):
    c = Usuario.objects.all()
    q = Reserva.objects.all()
    r = ReservaUsuario.objects.get(pk = id)
    contexto = {'data': r, 'usuario' : c, 'reserva': q }
    return render(request, 'planning_travel/reservas_usuarios/reservas_usuarios_form_editar.html', contexto)

def reservas_usuarios_actualizar(request):
    if request.method == 'POST': 
        id = request.POST.get('id')    
        usuario = Usuario.objects.get(pk=request.POST.get('usuario'))
        reserva = Reserva.objects.get(pk=request.POST.get('reserva'))
        estado_reserva = request.POST.get('estado_reserva')
        fecha_realizacion = request.POST.get('fecha_realizacion')
        try:
            q = ReservaUsuario.objects.get(pk = id)
            q.usuario = usuario
            q.reserva = reserva
            q.estado_reserva = estado_reserva
            q.fecha_realizacion = fecha_realizacion

            q.save()
            messages.success(request, "Fue actualizado correctamente")

        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('reservas_usuarios_listar')

#Crud HotelCategoria
def hoteles_categorias(request):
    q = HotelCategoria.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/hoteles_categorias/hoteles_categorias.html', contexto)

def hoteles_categorias_form(request):
    q = Hotel.objects.all()
    c = Categoria.objects.all()
    contexto = {'data': q, 'categoria': c}
    return render(request, 'planning_travel/hoteles_categorias/hoteles_categorias_form.html', contexto)

def hoteles_categorias_crear(request):
    if request.method == 'POST':
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        categoria = Categoria.objects.get(pk=request.POST.get('categoria'))
        try:
            q = HotelCategoria(
                id_hotel = hotel,
                id_categoria = categoria,
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('hoteles_categorias_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('hoteles_categorias_listar')
    
def hoteles_categorias_eliminar(request, id):
    try:
        q = HotelCategoria.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Hoteles categorias eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')
    
    return redirect("hoteles_categorias_listar") 

def hoteles_categorias_form_editar(request, id):
    c = Hotel.objects.all()
    q = Categoria.objects.all()
    r = HotelCategoria.objects.get(pk = id)
    contexto = {'data': r, 'hotel' : c, 'categoria': q }
    return render(request, 'planning_travel/hoteles_categorias/hoteles_categorias_form_editar.html', contexto)

def hoteles_categorias_actualizar(request):
    if request.method == 'POST': 
        id = request.POST.get('id')    
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        categoria = Categoria.objects.get(pk=request.POST.get('categoria'))
        try:
            q = HotelCategoria.objects.get(pk = id)
            q.id_hotel = hotel
            q.id_categoria = categoria
            q.save()
            messages.success(request, "Fue actualizado correctamente")

        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('hoteles_categorias_listar')

# Crud de fotos
def fotos(request):
    q = Foto.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/fotos/fotos.html', contexto)

def fotos_form(request):
    q = Hotel.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/fotos/fotos_form.html', contexto)

def fotos_crear(request):
    if request.method == 'POST':
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        url = request.FILES.get('url')
        descripcion = request.POST.get('descripcion')
        try:
            q = Foto(
                id_hotel=hotel,
                url_foto=url,
                descripcion=descripcion
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('fotos_listar')

def fotos_eliminar(request, id):
    try:
        q = Foto.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Foto eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('fotos_listar')

def fotos_form_editar(request, id):
    q = Foto.objects.get(pk = id)
    h = Hotel.objects.all()
    contexto = {'data': q, 'hotel': h}
    return render(request, 'planning_travel/fotos/fotos_form_editar.html', contexto)

def fotos_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        url = request.FILES.get('url')
        descripcion = request.POST.get('descripcion')
        try:
            q = Foto.objects.get(pk = id)
            q.id_hotel = hotel
            q.url_foto = url
            q.descripcion = descripcion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('hoteles_listar')

# Crud de HotelComodidad
def hoteles_comodidades(request):
    q = HotelComodidad.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/hoteles_comodidades/hoteles_comodidades.html', contexto)

def hoteles_comodidades_form(request):
    q = Hotel.objects.all()
    c = Comodidad.objects.all()
    contexto = {'hotel': q, 'comodidad': c}
    return render(request, 'planning_travel/hoteles_comodidades/hoteles_comodidades_form.html', contexto)

def hoteles_comodidades_crear(request):
    if request.method == 'POST':
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        comodidad = Comodidad.objects.get(pk=request.POST.get('comodidad'))
        dispone = request.POST.get('dispone')
        dispone = True if dispone == 'on' else False
        try:
            q = HotelComodidad(
                id_hotel=hotel,
                id_comodidad=comodidad,
                dispone=dispone
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('hoteles_comodidades_listar')

def hoteles_comodidades_eliminar(request, id):
    try:
        q = HotelComodidad.objects.get(pk = id)
        q.delete()
        messages.success(request, 'HotelComodidad eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('hoteles_comodidades_listar')

def hoteles_comodidades_form_editar(request, id):
    q = HotelComodidad.objects.get(pk = id)
    h = Hotel.objects.all()
    c = Comodidad.objects.all()
    contexto = {'data': q, 'hotel': h, 'comodidad': c}
    return render(request, 'planning_travel/hoteles_comodidades/hoteles_comodidades_form_editar.html', contexto)

def hoteles_comodidades_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        hotel = Hotel.objects.get(pk=request.POST.get('hotel'))
        comodidad = Comodidad.objects.get(pk=request.POST.get('comodidad'))
        dispone = request.POST.get('dispone')
        dispone = True if dispone == 'on' else False
        try:
            q = HotelComodidad.objects.get(pk = id)
            q.id_hotel = hotel
            q.id_comodidad = comodidad
            q.dispone = dispone
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('hoteles_comodidades_listar')


#andres
def cambiar_clave(request):
    if request.method == "POST":
        logueo = request.session.get("logueo", False)
        q = Usuario.objects.get(pk=logueo["id"])
        c1 = request.POST.get("nueva1")
        c2 = request.POST.get("nueva2")
        if verify_password(request.POST.get("clave"), q.password):
            if c1 == c2:
                # cambiar clave en DB
                q.password = make_password(c1)
                q.save()
                messages.success(request, "Contraseña guardada correctamente!!")
            else:
                messages.info(request, "Las contraseñas nuevas no coinciden...")
        else:
            messages.error(request, "Contraseña no válida...")
    else:
        messages.warning(request, "Error: No se enviaron datos...")

    return redirect('ver_perfil')

def ver_perfil(request):
	logueo = request.session.get("logueo", False)
	# Consultamos en DB por el ID del usuario logueado....
	q = Usuario.objects.get(pk=logueo["id"])
	contexto = {"data": q}
	return render(request, "planning_travel/login/perfil_usuario.html", contexto)





def perfil_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        print(f"Nombre: {nombre}")  # Debug print

        try:
            # Obtén el objeto Usuario por su ID
            usuario = Usuario.objects.get(pk=id)
            usuario.nombre = nombre
            usuario.apellido = apellido 
            usuario.email = correo
            usuario.save()
            messages.success(request, "Perfil actualizado correctamente")
            
            return redirect('ver_perfil')  # Redirecciona a una página después de la actualización
        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe")
        except Exception as e:
            messages.error(request, f'Error: {e}')
    else:
        messages.warning(request, 'No se enviaron datos')
    return redirect('ver_perfil')





# Crud de Reservas
def reservas(request):
    q = Reserva.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/reservas/reservas.html', contexto)

def reservas_form(request):
    q = Habitacion.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/reservas/reservas_form.html', contexto)

def reservas_crear(request):
    if request.method == 'POST':
        habitacion = Habitacion.objects.get(pk=request.POST.get('habitacion'))
        fecha_llegada = request.POST.get('fecha_llegada')
        fecha_salida = request.POST.get('fecha_salida')
        cantidad_personas = request.POST.get('cantidad_personas')
        print(fecha_llegada)
        try:
            q = Reserva(
                habitacion=habitacion,
                fecha_llegada=fecha_llegada,
                fecha_salida=fecha_salida,
                cantidadPersonas=cantidad_personas
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('reservas_listar')

def reservas_eliminar(request, id):
    try:
        q = Reserva.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Reserva eliminada correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('reservas_listar')

def reservas_form_editar(request, id):
    q = Reserva.objects.get(pk = id)
    h = Habitacion.objects.all()
    contexto = {'data': q, 'habitacion': h}
    return render(request, 'planning_travel/reservas/reservas_form_editar.html', contexto)

def reservas_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        habitacion = Habitacion.objects.get(pk=request.POST.get('habitacion'))
        fecha_llegada = request.POST.get('fecha_llegada')
        fecha_salida = request.POST.get('fecha_salida')
        cantidad_personas = request.POST.get('cantidad_personas')
        try:
            q = Reserva.objects.get(pk = id)
            q.id_habitacion = habitacion
            q.fecha_llegada = fecha_llegada
            q.fecha_salida = fecha_salida
            q.cantidadPersonas = cantidad_personas
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('reservas_listar')

# Crud reportes
def reportes(request):
    consulta = Reporte.objects.all()
    context = {'data': consulta}
    return render(request, 'planning_travel/reportes/reportes.html', context)

def reportes_form(request):
    q = Usuario.objects.all()
    context = {'usuario': q}
    return render(request, 'planning_travel/reportes/reportes_form.html', context)

def reportes_crear(request):
    if request.method == 'POST':
        id_usuario =Usuario.objects.get(pk = request.POST.get('id_usuario'))
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Reporte(
                id_usuario=id_usuario,
                nombre= nombre,
                descripcion= descripcion
            )
            q.save()
            messages.success(request, "El reporte fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('reportes_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('reportes_listar')

def reportes_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id_usuario =Usuario.objects.get(pk = request.POST.get('id_usuario'))
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        try:
            q = Reporte.objects.get(pk = id)
            q.id_usuario=id_usuario
            q.nombre = nombre
            q.descripcion = descripcion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('reportes_listar')

def reportes_eliminar(request, id):
    try:
        q = Reporte.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Reporte eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('reportes_listar')

def reportes_form_editar(request, id):
    q = Usuario.objects.all()
    r = Reporte.objects.get(pk = id)
    context = { 'usuario' : q , 'data' : r }
    return render(request, 'planning_travel/reportes/reportes_form_editar.html', context)

# Crud reportes moderador
def reportes_moderador(request):
    q = ReporteModerador.objects.all()
    context = {'data': q}
    return render(request, 'planning_travel/reportes_moderador/reportes_moderador.html', context)

def reportes_moderador_form(request):
    q = Usuario.objects.all()
    r = Reporte.objects.all()
    context = { 'usuario' : q , 'reporte' : r }
    return render(request, 'planning_travel/reportes_moderador/reportes_moderador_form.html', context)

def reportes_moderador_crear(request):
    if request.method == 'POST':
        id_usuario = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        id_reporte = Reporte.objects.get(pk = request.POST.get('id_reporte'))
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        try:
            q = ReporteModerador(
                id_usuario=id_usuario,
                id_reporte=id_reporte,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('reportes_moderador_listar')

def reportes_moderador_eliminar(request, id):
    try:
        q = ReporteModerador.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Reporte eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('reportes_moderador_listar')

def reportes_moderador_form_editar(request, id):
    q = ReporteModerador.objects.get(pk = id)
    u = Usuario.objects.all()
    r = Reporte.objects.all()
    context = {'data': q, 'usuario': u, 'reporte':r}
    return render(request, 'planning_travel/reportes_moderador/reportes_moderador_form_editar.html', context)

def reportes_moderador_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id_reporte = Reporte.objects.get(pk = request.POST.get('id_reporte'))
        id_usuario = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        try:
            q = ReporteModerador.objects.get(pk = id)
            q.fecha_inicio = fecha_inicio
            q.fecha_fin = fecha_fin
            q.id_reporte = id_reporte
            q.id_usuario = id_usuario
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('reportes_moderador_listar')

# Crud cliente
def clientes(request):
    q = Cliente.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/clientes/clientes.html', contexto)

def clientes_form(request):
    q = Usuario.objects.all()
    context= {'data': q}
    return render(request, 'planning_travel/clientes/clientes_form.html', context)

def clientes_crear(request):
    if request.method == 'POST':
        id_usuario = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        nombre = request.POST.get('nombre')
        numero_contacto = request.POST.get('numero_contacto')
        fotoPerfil = request.POST.get('fotoPerfil')
        try:
            q = Cliente(
                id_usuario=id_usuario,
                nombre=nombre,
                numero_contacto=numero_contacto,
                fotoPerfil=fotoPerfil
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'error')
    return redirect('clientes_listar')

def clientes_eliminar(request, id):
    try:
        q = Cliente.objects.get(pk = id)
        q.delete()
        messages.success(request, 'cliente eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('clientes_listar')

def clientes_form_editar(request, id):
    q = Cliente.objects.get(pk = id)
    c = Usuario.objects.all()
    context = { 'data': q , 'usuario': c }
    return render(request, 'planning_travel/clientes/clientes_form_editar.html', context)

def clientes_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id_usuario  = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        nombre = request.POST.get('nombre')
        numero_contacto = request.POST.get('numero_contacto')
        fotoPerfil = request.POST.get('fotoPerfil')
        try:
            q = Cliente.objects.get(pk = id)
            q.nombre = nombre
            q.id_usuario = id_usuario
            q.numero_contacto = numero_contacto            
            q.fotoPerfil = fotoPerfil
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('clientes_listar')

# Crud perfil Usuario
def perfil_usuarios(request):
    q = PerfilUsuario.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/perfil_usuarios/perfil_usuarios.html', contexto)

def perfil_usuarios_form(request):
    q = Usuario.objects.all()
    h = Hotel.objects.all()
    context = { 'usuarios' : q , 'hotel' : h }
    return render(request, 'planning_travel/perfil_usuarios/perfil_usuarios_form.html', context)

def perfil_usuarios_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        numero_contacto = request.POST.get('numero_contacto')
        id_usuario = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        id_hotel = Hotel.objects.get(pk = request.POST.get('id_hotel'))
        fotoPerfil = request.POST.get('fotoPerfil')
        try:
            q = PerfilUsuario(
                nombre=nombre,
                numero_contacto=numero_contacto,
                id_hotel=id_hotel,
                id_usuario=id_usuario,
                fotoPerfil=fotoPerfil
            )
            q.save()
            messages.success(request, "Fue creado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'error')
    return redirect('perfil_usuarios_listar')

def perfil_usuarios_eliminar(request, id):
    try:
        q = PerfilUsuario.objects.get(pk = id)
        q.delete()
        messages.success(request, 'eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('perfil_usuarios_listar')

def perfil_usuarios_form_editar(request, id):
    q = PerfilUsuario.objects.get(pk = id)
    u = Usuario.objects.all()
    h = Hotel.objects.all()
    context = {'data': q , 'hotel': h, 'usuarios' : u}
    return render(request, 'planning_travel/perfil_usuarios/perfil_usuarios_form_editar.html', context)

def perfil_usuarios_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id_usuario = Usuario.objects.get(pk = request.POST.get('id_usuario'))
        id_hotel = Hotel.objects.get(pk = request.POST.get('id_hotel'))
        nombre = request.POST.get('nombre')
        numero_contacto = request.POST.get('numero_contacto')
        fotoPerfil = request.POST.get('fotoPerfil')
        try:
            q = PerfilUsuario.objects.get(pk = id)
            q.id_usuario = id_usuario
            q.id_hotel = id_hotel
            q.nombre = nombre
            q.numero_contacto = numero_contacto            
            q.fotoPerfil = fotoPerfil
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
    return redirect('perfil_usuarios_listar')

# # Crud Comentarios
# def comentarios(request):
#     q = Comentario.objects.all()
#     e = Hotel.objects.all()
#     c = Usuario.objects.all()
#     contexto = {'data': q, 'usuario': c}
#     return render(request, 'planning_travel/comentarios/comentarios.html', contexto)

# def comentarios_form(request):
#     q = Hotel.objects.all()
#     c = Usuario.objects.all()
#     contexto = {'data': q, 'usuario': c}
#     return render(request, 'planning_travel/comentarios/comentarios_form.html',contexto)

# def comentarios_crear(request):
#     if request.method == 'POST':
#         id_hotel = Hotel.objects.get(pk=request.POST.get('id_hotel'))
#         id_usuario = Usuario.objects.get(pk=request.POST.get('id_usuario'))
#         contenido = request.POST.get('contenido')
#         fecha = request.POST.get('fecha')

#         try:
#             q = Comentario(
#                 id_hotel=id_hotel,
#                 id_usuario=id_usuario,
#                 contenido=contenido,
#                 fecha=fecha
#             )
#             q.save()
#             messages.success(request, "Fue agregado correctamente")
#         except Exception as e:
#             messages.error(request,f'Error: {e}')

#         return redirect('comentarios_listar')
#     else:
#         messages.warning(request,'No se enviaron datos')
#         return redirect('comentarios_listar')

# def comentarios_eliminar(request, id):
#     try:
#         q = Comentario.objects.get(pk = id)
#         q.delete()
#         messages.success(request, 'Comentario eliminado correctamente!!')
#     except Exception as e:
#         messages.error(request,f'Error: {e}')

#     return redirect('comentarios_listar')

# def comentarios_form_editar(request, id):
#     q = Comentario.objects.get(pk = id)
#     c = Hotel.objects.all()
#     e = Usuario.objects.all()
#     contexto = {'data': q, 'hotel': c, 'usuario': e}
#     return render(request, 'planning_travel/comentarios/comentarios_form_editar.html', contexto)

# def comentarios_actualizar(request):
'''
    if request.method == 'POST':
        id = request.POST.get('id')
        id_hotel = Hotel.objects.get(pk=request.POST.get("id_hotel"))
        id_usuario = Usuario.objects.get(pk=request.POST.get("id_usuario"))
        contenido = request.POST.get('contenido')
        fecha = request.POST.get('fecha')
        print(fecha)

        try:
            q = Comentario.objects.get(pk = id)
            q.id_hotel = id_hotel
            q.id_usuario = id_usuario
            q.contenido = contenido
            q.fecha = fecha
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('comentarios_listar')
'''
'''
# Crud Roles
def roles(request):
    consulta = Rol.objects.all()
    context = {'data': consulta}
    return render(request, 'planning_travel/roles/roles.html', context)

def roles_form(request):
    return render(request, 'planning_travel/roles/roles_form.html')

def roles_crear(request):
    if request.method == 'POST':
        nombre= request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        permisos = request.POST.get('permisos')

        try:
            q = Rol(
                nombre=nombre,
                descripcion=descripcion,
                permisos=permisos,
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('roles_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('roles_listar')

def roles_eliminar(request, id):
    try:
        q = Rol.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Rol eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('roles_listar')

def roles_formulario_editar(request, id):

    q = Rol.objects.get(pk = id)
    contexto = {'data': q}

    return render(request, 'planning_travel/roles/roles_form_editar.html', contexto)

def roles_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre= request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        permisos = request.POST.get('permisos')

        try:
            q = Rol.objects.get(pk = id)
            q.nombre= nombre
            q.descripcion = descripcion
            q.permisos = permisos
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

    else:
            messages.warning(request,'No se enviaron datos')
    return redirect('roles_listar')
'''
# Crud favoritos
def favoritos(request):
    consulta = Favorito.objects.all()
    context = {'data': consulta}
    return render(request, 'planning_travel/favoritos/favoritos.html', context)

def favoritos_form(request):
    q = Hotel.objects.all()
    c = Usuario.objects.all()
    contexto = {'data': q, 'usuario': c}
    return render(request, 'planning_travel/favoritos/favoritos_form.html', contexto)

def favoritos_crear(request):
    if request.method == 'POST':
        id_hotel = Hotel.objects.get(pk=request.POST.get('id_hotel'))
        id_usuario = Usuario.objects.get(pk=request.POST.get('id_usuario'))
        fecha_agregado = request.POST.get('fecha_agregado')

        try:
            q = Favorito(
                id_hotel=id_hotel,
                id_usuario=id_usuario,
                fecha_agregado=fecha_agregado,
            )
            q.save()
            messages.success(request, "Fue agregado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')

        return redirect('favoritos_listar')
    else:
        messages.warning(request,'No se enviaron datos')
        return redirect('favoritos_listar')

def favoritos_eliminar(request, id):
    try:
        q = Favorito.objects.get(pk = id)
        q.delete()
        messages.success(request, 'Hotel favorito eliminado correctamente!!')
    except Exception as e:
        messages.error(request,f'Error: {e}')

    return redirect('favoritos_listar')

def favoritos_formulario_editar(request, id):
    q = Favorito.objects.get(pk = id)
    c = Hotel.objects.all()
    e = Usuario.objects.all()
    contexto = {'data': q, 'hotel': c, 'usuario': e}
    return render(request, 'planning_travel/favoritos/favoritos_form_editar.html', contexto)

def favoritos_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        id_hotel = Hotel.objects.get(pk=request.POST.get("id_hotel"))
        id_usuario = Usuario.objects.get(pk=request.POST.get("id_usuario"))
        fecha_agregado = request.POST.get('fecha_agregado')

        try:
            q = Favorito.objects.get(pk = id)
            q.id_hotel= id_hotel
            q.id_usuario = id_usuario
            q.fecha_agregado=fecha_agregado
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')
        
    return redirect('favoritos_listar')

# api base de datos
class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class HotelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class ComodidadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Comodidad.objects.all()
    serializer_class = ComodidadSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class FavoritoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSeralizer

class OpinionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer

# class ComentarioViewSet(viewsets.ModelViewSet):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer

# class PuntuacionViewSet(viewsets.ModelViewSet):
#     queryset = Puntuacion.objects.all()
#     serializer_class = PuntuacionSerializer

class FotoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Foto.objects.all()
    serializer_class = FotoSerializer

class HotelComodidadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = HotelComodidad.objects.all()
    serializer_class = HotelComodidadSerializer

class HotelCategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = HotelCategoria.objects.all()
    serializer_class = HotelCategoriaSerializer

class HabitacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class ReservaUsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ReservaUsuario.objects.all()
    serializer_class = ReservaUsuarioSerializer

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ReporteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer

class ReporteModeradorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ReporteModerador.objects.all()
    serializer_class = ReporteModeradorSerializer
