const fechaLlegada = document.querySelector('#fecha_llegada');
const fechaSalida = document.querySelector('#fecha_salida');
fechaLlegada.addEventListener('change', () => {
    if(fechaLlegada !== '') {
        $(fechaSalida).prop('disabled', false);
    }
    // console.log(formatDate(addDay(fechaLlegada.value)));
    fechaSalida.setAttribute('min', formatDate(sumaFecha(fechaLlegada.value)));
    console.log(formatDate(sumaFecha(fechaLlegada.value)))
    // console.log(fechaLlegada.value);
    // console.log(formatDateToISO(sumaFecha(fechaLlegada.value)));
});

function verificarDisponibilidad(url) {
    const csrftoken = getCookie('csrftoken');

    // Limpiar mensajes de disponibilidad y restablecer botones antes de la verificación
    $('.mensaje-disponibilidad').remove(); // Limpiar todos los mensajes
    $(".habitacion").prop('disabled', false).removeClass('habitacion-ocupada'); // Habilitar todos los botones y quitar la clase

    $.ajax({
        url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        ContentType: 'application/json',
        data: {
            'fecha_llegada': fechaLlegada.value,
            'fecha_salida': fechaSalida.value
        }
    })
    .done(function(data) {
        const habitacionesOcupadas = data.habitaciones_ocupadas;
        console.log(data);

        // Variable para determinar si hay habitaciones disponibles
        let hayDisponibles = true;

        habitacionesOcupadas.forEach(numHabitacion => {
            const habitacionElement = $(`#habitacion-${numHabitacion}`);
            const parent = habitacionElement.parent();

            // Deshabilitar el botón y agregar la clase de ocupada
            habitacionElement.prop('disabled', true);
            habitacionElement.addClass('habitacion-ocupada');

            hayDisponibles = false; // Si hay habitaciones ocupadas, cambia el estado
        });

        // Mostrar mensaje de disponibilidad
        const mensaje = $('<div class="mensaje-disponibilidad"></div>');
        if (hayDisponibles) {
            mensaje.text('Todas las habitaciones están disponibles.').addClass('disponible');
        } else {
            mensaje.text('Algunas habitaciones no están disponibles.').addClass('no-disponible');
        }

        // Añadir el mensaje a un lugar visible
        $('#mensaje-global').html(mensaje); // Asegúrate de tener un contenedor con este ID
    })
    .fail(function(xhr, textStatus, errorThrown) {
        console.error(`Error al verificar disponibilidad ${errorThrown}`);
    });
}





function mostrarHabitacionesDisponibles(habitacionesDisponibles) {
    // Obtener todas las habitaciones en el formulario
    const habitacionesFormulario = document.querySelectorAll(".habitacion");

    // Convertir el array de habitaciones disponibles a un conjunto para una búsqueda más eficiente
    const habitacionesDisponiblesSet = new Set(habitacionesDisponibles);

    // Iterar sobre todas las habitaciones en el formulario
    habitacionesFormulario.forEach(function(habitacion) {
        // Obtener el número de la habitación desde el atributo data
        const numHabitacion = habitacion.getAttribute("data-num-habitacion");
        // Verificar si la habitación está disponible
        if (!habitacionesDisponiblesSet.has(numHabitacion)) {
            // Si la habitación no está disponible, aplicar la clase inactive
            habitacion.classList.add("inactive");
        } else {
            // Si la habitación está disponible, asegurarse de que no tenga la clase inactive
            habitacion.classList.remove("inactive");
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    $('.habitaciones').addClass('habitacion-disponible');
    const date = new Date();
    fechaLlegada.setAttribute('min', formatDate(date));
    
});

function obtenerTotal(url, id) {
    // Obtener el precio por noche
    $.ajax({
        url,
        type: 'GET',
        data: {'habitacion': id},
        success: function(response) {
            const fechaLlegada = new Date($('#fecha_llegada').val());
            const fechaSalida = new Date($('#fecha_salida').val());
            
            // Comprobar si ambas fechas están seleccionadas
            if (!isNaN(fechaLlegada) && !isNaN(fechaSalida) && fechaSalida > fechaLlegada) {
                const cantidadDias = (fechaSalida - fechaLlegada) / (1000 * 60 * 60 * 24); // Convertir a días
                const total = precioPorNoche * cantidadDias;
            }
        },
    });
}



function formatDate(date) {
    // Asegurarse de que 'date' sea un objeto Date válido
    if (!(date instanceof Date)) {
        date = new Date(date);
    }

    // Obtener los componentes de la fecha
    var year = date.getFullYear();
    var month = ('0' + (date.getMonth() + 1)).slice(-2); // Los meses van de 0 a 11
    var day = ('0' + date.getDate()).slice(-2);

    // Formato 'yyyy-mm-dd'
    var formattedDate = year + '-' + month + '-' + day;
    
    return formattedDate;
}

function addDay(date) {
    // Crear una copia de la fecha para no modificar la original
    console.log(date);
    var newDate = new Date(date);

    // Obtener el día actual
    var currentDay = newDate.getDate();

    // Establecer el día al siguiente
    newDate.setDate(currentDay + 1);

    // Si el día es igual al día original, significa que era el último día del mes
    // En este caso, ajustar al primer día del siguiente mes
    if (newDate.getDate() === currentDay) {
        newDate.setMonth(newDate.getMonth() + 1);
        newDate.setDate(1);
    }

    return newDate;
}

function sumaFecha(fecha) {
    let fechaNow = new Date(fecha);
    fechaNow.setSeconds(86400*2);
    return `${fechaNow.getFullYear()}-${fechaNow.getMonth()+1}-${fechaNow.getDate()}`;
}
