    const images = document.querySelectorAll('#image-container img');
    let current = 0;

setInterval(() => {
    // Oculta imagen actual
    images[current].classList.remove('opacity-100');
    images[current].classList.add('opacity-0');

    // Avanza a la siguiente imagen
    current = (current + 1) % images.length;

    // Muestra la nueva imagen
    images[current].classList.remove('opacity-0');
    images[current].classList.add('opacity-100');
  }, 5000); // Cambia cada 3 segundos