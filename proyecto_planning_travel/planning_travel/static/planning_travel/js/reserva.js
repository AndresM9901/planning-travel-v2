function verificarDisponibilidad(url) {
    console.log(url);
    const fechaLlegada = document.querySelector('#fecha_llegada').value;
    const fechaSalida = document.querySelector('#fecha_salida').value;
    const csrftoken = getCookie('csrftoken');
    console.log(fechaLlegada);

    $.ajax({
        url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        ContentType: 'application/json',
        data: {
            'fecha_llegada': fechaLlegada,
            'fecha_salida': fechaSalida
        }
    })
    .done(function(data) {
        const habitacionesOcupadas = data.habitaciones_ocupadas;
        const habitacionesDisponibles = data.habitaciones_disponibles;
        console.log(data);
        habitacionesOcupadas.forEach(numHabitacion => {
            $(`#habitacion-${numHabitacion}`).parent().addClass('habitacion-ocupada');
            $(`#habitacion-${numHabitacion}`).parent().removeClass('habitacion-disponible');
            $(`#habitacion-${numHabitacion}`).prop('disabled', true);
            if($(`#habitacion-${numHabitacion}`).parent().hasClass('habitacion-ocupada')) {
                $(`#habitacion-${numHabitacion}`).parent().append('<i class="bi bi-house-dash-fill i-ocupado"></i>');
            }
        });
        habitacionesDisponibles.forEach(numHabitacion => {
            $(`#habitacion-${numHabitacion}`).parent().append('<i class="bi bi-house-check-fill i-disponible"></i>');
        })
    })
    .fail(function(xhr, textStatus, errorThrown) { // Cambiar error por xhr, textStatus, errorThrown
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
});

function obtenerTotal(url, id) {
    $.ajax({
        url,
        type: 'GET',
        data: {'habitacion': id},
        success: function(response) {
            $('#total').text(`Total: ${response.precio}`)
        },
        error: function(error) {
            console.log(error);
        }
    });
}