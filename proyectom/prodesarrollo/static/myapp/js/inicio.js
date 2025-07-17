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



function toggleMenu() {
    const menu = document.getElementById("dropdownMenu");
    menu.classList.toggle("hidden");
}

  // Opcional: cerrar si haces clic fuera
document.addEventListener("click", function (event) {
    const menu = document.getElementById("dropdownMenu");
    const button = event.target.closest("button");
    if (!menu.contains(event.target) && !button) {
    menu.classList.add("hidden");
    }
});



  function previewImage(event) {
    const preview = document.getElementById('preview');
    const reader = new FileReader();
    reader.onload = function () {
      preview.src = reader.result;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(event.target.files[0]);
  }