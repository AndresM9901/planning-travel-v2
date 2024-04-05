from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from .serializers import *
from rest_framework import viewsets
from django.db.models import Min

# Create your views here.

def inicio(request):
    # Obtener todos los hoteles, fotos y servicios
    hoteles = Hotel.objects.all()
    fotos = Foto.objects.all()
    servicios = Servicio.objects.all()
    servicio_activo = None
    
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
    return render(request, 'planning_travel/hoteles/hotel_home/hotel_home.html', {'hoteles': hoteles_con_fotos, 'servicios': servicios, 'servicio_activo': servicio_activo})

def detalle_hotel(request, id):
    hotel = Hotel.objects.get(pk=id)
    servicios_hotel = HotelServicio.objects.filter(id_hotel=id)
    servicios = []
    for servicio in servicios_hotel:
        sq = Servicio.objects.get(id=servicio.id_servicio.id)
        servicios.append(sq)
    habitaciones = Habitacion.objects.filter(id_hotel=id)
    fotos = Foto.objects.filter(id_hotel=id)
    contexto = {
        'hotel': hotel,
        'servicios': servicios,
        'habitaciones': habitaciones,
        'fotos': fotos
    }
    return render(request, 'planning_travel/hoteles/hotel_home/hotel_detail.html', contexto)


# def inicio(request):
#     hoteles = Hotel.objects.all()
#     fotos = Foto.objects.all()
#     servicios = Servicio.objects.all()
    
#     servicio_id = request.GET.get('servicio')
#     if servicio_id:
#         # hoteles_servicio = HotelServicio.objects.filter(id_servicio=servicio_id)
#         # print(hoteles_servicio)
#         # hoteles = [hotel for hotel in hoteles if hotel.id in hoteles_servicio]
#         # print(hoteles)
#         hoteles_servicio = HotelServicio.objects.filter(id_servicio=servicio_id)
#         hoteles_ids = [hs.id_hotel_id for hs in hoteles_servicio]
#         hoteles = hoteles.filter(id__in=hoteles_ids)

#     for hotel in hoteles:
#         # Obtener la cantidad de opiniones
#         opiniones_count = Opinion.objects.filter(id_hotel=hotel.id).count()
#         # Obtener el promedio de valoración
#         valoraciones = Opinion.objects.filter(id_hotel=hotel.id).values_list('puntuacion', flat=True)
#         promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0

#         hotel.opiniones_count = opiniones_count
#         hotel.promedio_valoracion = promedio_valoracion
    
#     fotos_por_hotel = {}
#     for foto in fotos:
#         fotos_por_hotel.setdefault(foto.id_hotel, []).append(foto)

#     hoteles_con_fotos = [(hotel, fotos_por_hotel.get(hotel.id, [])) for hotel in hoteles]

#     context = {'hoteles': hoteles_con_fotos, 'servicios': servicios}
#     return render(request, 'planning_travel/hoteles/hotel_home/hotel_home.html', context)

# def inicio(request):
#     hoteles = Hotel.objects.all()
#     fotos = Foto.objects.all()
#     servicios = Servicio.objects.all()
    
#     for hotel in hoteles:
#         # Obtener la cantidad de opiniones
#         opiniones_count = Opinion.objects.filter(id_hotel=hotel.id).count()
#         # Obtener el promedio de valoración
#         valoraciones = Opinion.objects.filter(id_hotel=hotel.id).values_list('puntuacion', flat=True)
#         promedio_valoracion = sum(valoraciones) / len(valoraciones) if valoraciones else 0

#         hotel.opiniones_count = opiniones_count
#         hotel.promedio_valoracion = promedio_valoracion
#     # Crea un diccionario para agrupar las fotos por ID de hotel
#     fotos_por_hotel = {}
#     for foto in fotos:
#         if foto.id_hotel not in fotos_por_hotel:
#             fotos_por_hotel[foto.id_hotel] = []
#         fotos_por_hotel[foto.id_hotel].append(foto)
        
#     hoteles_con_fotos = [(hotel, fotos_por_hotel.get(hotel, [])) for hotel in hoteles]
#     # Envía los datos a la plantilla 'hoteles': hoteles, 'fotos_por_hotel': fotos_por_hotel
#     return render(request, 'planning_travel/hoteles/hotel_home/hotel_home.html', {'hoteles': hoteles_con_fotos, 'servicios': servicios})

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
        messages.warning(request,'No se enviaron datos')
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

def index(request):
    return render(request, 'planning_travel/login/login.html')

# Crud de Usuarios

def usuarios(request):
    q = Usuario.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/login/usuarios.html', contexto)

def usuarios_form(request):
    q = Rol.objects.all()
    contexto = {'data': q}
    return render(request, 'planning_travel/login/usuarios_form.html', contexto)

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
        rol = Rol.objects.get(pk=request.POST.get('rol'))
        foto = request.POST.get('foto')
        try:
            q = Usuario.objects.get(pk = id)
            q.nombre = nombre
            q.correo = correo
            q.contrasena = contrasena
            q.rol = rol
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
    contexto = {'data': q}
    return render(request, 'planning_travel/hoteles/hoteles_form.html', contexto)

def hoteles_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        categoria = Categoria.objects.get(pk=request.POST.get('categoria'))
        cantidad_habitacion = request.POST.get('cantidad_habitacion')
        try:
            q = Hotel(
                nombre=nombre,
                descripcion=descripcion,
                direccion=direccion,
                categoria=categoria,
                cantidad_habitacion=cantidad_habitacion,
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

# Crud de puntuacion

# def puntuaciones(request):
#     q = Puntuacion.objects.all()
#     contexto = {'data': q}
#     return render(request, 'planning_travel/puntuaciones/puntuaciones.html', contexto)

# def puntuaciones_form(request):
#     q = Comentario.objects.all()
#     contexto = {'data': q}
#     return render(request, 'planning_travel/puntuaciones/puntuaciones_form.html', contexto)

# def puntuaciones_crear(request):
#     if request.method == 'POST':
#         comentario = Comentario.objects.get(pk=request.POST.get('comentario'))
#         valoracion = request.POST.get('valoracion')
#         try:
#             q = Puntuacion(
#                 comentario=comentario,
#                 valoracion=valoracion,
#             )
#             q.save()
#             messages.success(request, "Fue actualizado correctamente")
#         except Exception as e:
#             messages.error(request,f'Error: {e}')

#         return redirect('puntuaciones_listar')
#     else:
#         messages.warning(request,'No se enviaron datos')
#         return redirect('puntuaciones_listar')
    
# def puntuaciones_eliminar(request, id):
#     try:
#         q = Puntuacion.objects.get(pk = id)
#         q.delete()
#         messages.success(request, 'Puntuacion eliminada correctamente!!')
#     except Exception as e:
#         messages.error(request,f'Error: {e}')
        
# def puntuaciones_form_editar(request, id):
#     q = Puntuacion.objects.get(pk = id)
#     c = Comentario.objects.all()
#     contexto = {'data': q, 'comentario': c}
#     return render(request, 'planning_travel/puntuaciones/puntuaciones_form_editar.html', contexto)

# def puntuaciones_actualizar(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        comentario = Comentario.objects.get(pk=request.POST.get('comentario'))
        valoracion = request.POST.get('valoracion')
        try:
            q = Usuario.objects.get(pk = id)
            q.comentario = comentario
            q.valoracion = valoracion
            q.save()
            messages.success(request, "Fue actualizado correctamente")
        except Exception as e:
            messages.error(request,f'Error: {e}')
    else:
        messages.warning(request,'No se enviaron datos')

    return redirect('puntuaciones_listar')

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
        id= request.POST.get('id')
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
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class ComodidadViewSet(viewsets.ModelViewSet):
    queryset = Comodidad.objects.all()
    serializer_class = ComodidadSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class FavoritoViewSet(viewsets.ModelViewSet):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSeralizer

class OpinionViewSet(viewsets.ModelViewSet):
    queryset = Opinion.objects.all()
    serializer_class = OpinionSerializer

# class ComentarioViewSet(viewsets.ModelViewSet):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer

# class PuntuacionViewSet(viewsets.ModelViewSet):
#     queryset = Puntuacion.objects.all()
#     serializer_class = PuntuacionSerializer

class FotoViewSet(viewsets.ModelViewSet):
    queryset = Foto.objects.all()
    serializer_class = FotoSerializer

class HotelComodidadViewSet(viewsets.ModelViewSet):
    queryset = HotelComodidad.objects.all()
    serializer_class = HotelComodidadSerializer

class HotelCategoriaViewSet(viewsets.ModelViewSet):
    queryset = HotelCategoria.objects.all()
    serializer_class = HotelCategoriaSerializer

class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class ReservaUsuarioViewSet(viewsets.ModelViewSet):
    queryset = ReservaUsuario.objects.all()
    serializer_class = ReservaUsuarioSerializer

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer

class ReporteModeradorViewSet(viewsets.ModelViewSet):
    queryset = ReporteModerador.objects.all()
    serializer_class = ReporteModeradorSerializer
