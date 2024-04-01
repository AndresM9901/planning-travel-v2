// // Galeria
// document.addEventListener('DOMContentLoaded', function() {
//     const imagenes = document.querySelectorAll('.item img');
//     const modal = document.getElementById('modal');
//     const modalImg = document.getElementById('modal-img');
//     const closeButton = document.getElementById('close-button');

//     imagenes.forEach(imagen => {
//         imagen.addEventListener('click', function() {
//             modal.style.display = 'block';
//             modalImg.src = this.src;
//         });
//     });

//     closeButton.addEventListener('click', function() {
//         modal.style.display = 'none';
//     });

//     modal.addEventListener('click', function(event) {
//         if (event.target === modal) {
//             modal.style.display = 'none';
//         }
//     });
// });

// Galeria 2
// Función para abrir el modal
// function openModal() {
//     document.getElementById('myModal').style.display = "block";
// }

// // Función para cerrar el modal
// function closeModal() {
//     document.getElementById('myModal').style.display = "none";
// }

// var slideIndex = 1;
// showSlides(slideIndex);

// // Función para avanzar o retroceder las diapositivas
// function plusSlides(n) {
//     showSlides(slideIndex += n);
// }

// // Función para mostrar la diapositiva actual
// function currentSlide(n) {
//     showSlides(slideIndex = n);
// }

// function showSlides(n) {
//     var i;
//     var slides = document.getElementsByClassName("mySlides");
//     if (n > slides.length) {slideIndex = 1}
//     if (n < 1) {slideIndex = slides.length}
//     for (i = 0; i < slides.length; i++) {
//         slides[i].style.display = "none";
//     }
//     slides[slideIndex-1].style.display = "block";
// }

document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carrusel');
    const thumbnails = document.querySelectorAll('.thumbnail');
    const prevBtn = document.querySelector('#prev');
    const nextBtn = document.querySelector('#next');
    let currentSlide = 0;
    

    function goToSlide(index) {
        carousel.scrollLeft = index * carousel.offsetWidth;
        setActiveThumbnail(index);
        currentSlide = index;
    }

    function setActiveThumbnail(index) {
        thumbnails.forEach((thumbnail, i) => {
            if (i === index) {
                thumbnail.classList.add('active');
            } else {
                thumbnail.classList.remove('active');
            }
        });
    }

    function prevSlide() {
        if (currentSlide > 0) {
            goToSlide(currentSlide - 1);
        }
    }
    
    function nextSlide() {
        if (currentSlide < thumbnails.length - 1) {
            goToSlide(currentSlide + 1);
        }
    }

    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => goToSlide(index));
    });
});

function selectSlide(index) {
    currentSlideIndex = index;
    updateCarousel();
    updateThumbnailsScroll();
}

function updateThumbnailsScroll() {
    var thumbnailsContainer = document.querySelector('.thumbnails-container');
    var selectedThumbnail = document.querySelector('.thumbnails img.active');
    var containerWidth = thumbnailsContainer.clientWidth;
    var thumbnailWidth = selectedThumbnail.clientWidth;
    var thumbnailOffset = selectedThumbnail.offsetLeft;

    var scrollLeft = thumbnailOffset - (containerWidth - thumbnailWidth) / 2;
    thumbnailsContainer.scrollLeft = scrollLeft;
}

