// // carusel
// const carousel = document.querySelector('.carrusel');
// const carouselItems = document.querySelectorAll('.carrusel-item');
// const totalItems = carouselItems.length;
// const indicatorsContainer = document.querySelector('.carrusel-indicators');
// const controlsContainer = document.querySelector('.carrusel-controls');
// let currentIndex = 0;

// function createIndicators() {
//     for (let i = 0; i < totalItems; i++) {
//         const indicator = document.createElement('div');
//         indicator.classList.add('carrusel-indicator');
//         if (i === currentIndex) {
//             indicator.classList.add('active');
//         }
//         indicator.addEventListener('click', () => {
//             currentIndex = i;
//             updateCarousel();
//         });
//         indicatorsContainer.appendChild(indicator);
//     }
// }

// function updateIndicators() {
//     const indicators = document.querySelectorAll('.carrusel-indicator');
//     indicators.forEach((indicator, index) => {
//         if (index === currentIndex) {
//             indicator.classList.add('active');
//         } else {
//             indicator.classList.remove('active');
//         }
//     });
// }

// function nextSlide() {
//     currentIndex = (currentIndex + 1) % totalItems;
//     updateCarousel();
// }

// function prevSlide() {
//     currentIndex = (currentIndex - 1 + totalItems) % totalItems;
//     updateCarousel();
// }

// function updateCarousel() {
//     const offset = -currentIndex * carouselItems[0].offsetWidth;
//     carousel.style.transform = `translateX(${offset}px)`;
//     updateIndicators();
// }

// createIndicators();

// const prevButton = document.querySelector('.carrusel-control.prev');
// const nextButton = document.querySelector('.carrusel-control.next');
// prevButton.addEventListener('click', prevSlide);
// nextButton.addEventListener('click', nextSlide);

// setInterval(nextSlide, 3000); // Auto-advance every 3 seconds


// document.addEventListener("DOMContentLoaded", function() {
//     const carousels = document.querySelectorAll('.carrusel');
//     carousels.forEach(carousel => {
//         const carouselItems = carousel.querySelectorAll('.carrusel-item');
//         const totalItems = carouselItems.length;
//         let currentIndex = 0;

//         function nextSlide() {
//             currentIndex = (currentIndex + 1) % totalItems;
//             updateCarousel();
//         }

//         function prevSlide() {
//             currentIndex = (currentIndex - 1 + totalItems) % totalItems;
//             updateCarousel();
//         }

//         function updateCarousel() {
//             const offset = -currentIndex * carouselItems[0].offsetWidth;
//             carousel.style.transform = `translateX(${offset}px)`;
//         }

//         const prevButton = carousel.closest('.card-hotel').querySelector('.prev');
//         const nextButton = carousel.closest('.card-hotel').querySelector('.next');
//         prevButton.addEventListener('click', prevSlide);
//         nextButton.addEventListener('click', nextSlide);

//         // Auto-advance every 3 seconds
//         setInterval(nextSlide, 3000);
//     });
// });


document.addEventListener("DOMContentLoaded", function() {
    const carousels = document.querySelectorAll('.carrusel');
    carousels.forEach(carousel => {
        const carouselItems = carousel.querySelectorAll('.carrusel-item');
        const totalItems = carouselItems.length;
        let currentIndex = 0;

        function createIndicators() {
            const indicatorsContainer = carousel.closest('.card-hotel').querySelector('.carrusel-indicators');
            for (let i = 0; i < totalItems; i++) {
                const indicator = document.createElement('div');
                indicator.classList.add('carrusel-indicator');
                if (i === currentIndex) {
                    indicator.classList.add('active');
                }
                indicator.addEventListener('click', () => {
                    currentIndex = i;
                    updateCarousel();
                });
                indicatorsContainer.appendChild(indicator);
            }
        }

        function updateIndicators() {
            const indicators = carousel.closest('.card-hotel').querySelectorAll('.carrusel-indicator');
            indicators.forEach((indicator, index) => {
                if (index === currentIndex) {
                    indicator.classList.add('active');
                } else {
                    indicator.classList.remove('active');
                }
            });
        }

        function nextSlide() {
            currentIndex = (currentIndex + 1) % totalItems;
            updateCarousel();
        }

        function prevSlide() {
            currentIndex = (currentIndex - 1 + totalItems) % totalItems;
            updateCarousel();
        }

        function updateCarousel() {
            const offset = -currentIndex * carouselItems[0].offsetWidth;
            carousel.style.transform = `translateX(${offset}px)`;
            updateIndicators();
        }

        createIndicators(); // Llama a la función para crear los indicadores al cargar la página
        updateIndicators(); // Actualiza los indicadores al cargar la página

        const prevButton = carousel.closest('.card-hotel').querySelector('.prev');
        const nextButton = carousel.closest('.card-hotel').querySelector('.next');
        prevButton.addEventListener('click', prevSlide);
        nextButton.addEventListener('click', nextSlide);

        // Auto-advance every 3 seconds
        // setInterval(nextSlide, 3000);
    });
});


function detallesDelHotel(url) {
    window.open(url, '_blank');
}