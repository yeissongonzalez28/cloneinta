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
function Menumas() {
    const menu = document.getElementById("MasMenu");
    menu.classList.toggle("hidden");
}
  // Opcional: cerrar si haces clic fuera
document.addEventListener("click", function (event) {
    const menu = document.getElementById("dropdownMenu , MasMenu");
    const button = event.target.closest("button");
    if (!menu.contains(event.target) && !button) {
    menu.classList.add("hidden");
    }
});

  document.addEventListener("DOMContentLoaded", function () {
    const abrirModalBtn = document.getElementById("abrirModal");
    const modal = document.getElementById("modalPublicacion");
    const cancelarBtn = document.getElementById("cancelarModal");

    abrirModalBtn.addEventListener("click", () => {
      modal.classList.remove("hidden");
    });

    cancelarBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
    });

    // Cierra el modal si se hace clic fuera del contenido
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.classList.add("hidden");
      }
    });
  });



document.getElementById('file-upload').addEventListener('change', function () {
  const container = document.getElementById('preview-container');
  container.innerHTML = '';

  Array.from(this.files).forEach(file => {
    const ext = file.name.split('.').pop().toLowerCase();
    const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);
    const isVideo = ['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext);

    const wrapper = document.createElement('div');
    wrapper.className = 'relative group';

    if (isImage) {
      const img = document.createElement('img');
      img.className = 'w-full h-32 object-cover rounded';
      img.src = URL.createObjectURL(file);
      wrapper.appendChild(img);
    } else if (isVideo) {
      const video = document.createElement('video');
      video.className = 'w-full h-32 rounded';
      video.controls = true;
      video.src = URL.createObjectURL(file);
      wrapper.appendChild(video);
    }

    container.appendChild(wrapper);
  });
});

// Opcional: cerrar modal
document.getElementById('cancelarModal')?.addEventListener('click', () => {
  document.getElementById('modalPublicacion').classList.add('hidden');
});


document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.video-container').forEach(container => {
    const video = container.querySelector('.video-player');
    const muteBtn = container.querySelector('.mute-toggle');
    const seekBar = container.querySelector('.seek-bar');

    // Reproducir o pausar al hacer click en el video
    video.addEventListener('click', () => {
      if (video.paused) {
        video.play();
      } else {
        video.pause();
      }
    });

    // Botón mute
    muteBtn.addEventListener('click', () => {
      video.muted = !video.muted;
      muteBtn.textContent = video.muted ? '🔇' : '🔊';
    });

    // Actualiza el seekBar mientras se reproduce
    video.addEventListener('timeupdate', () => {
      if (!isNaN(video.duration)) {
        seekBar.value = (video.currentTime / video.duration) * 100;
      }
    });

    // Cambiar tiempo al mover el slider
    seekBar.addEventListener('input', () => {
      const time = (seekBar.value / 100) * video.duration;
      video.currentTime = time;
    });

    // Reproducir/pausar según visibilidad
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          video.play().catch(e => {}); // En algunos navegadores puede fallar por autoplay
        } else {
          video.pause();
        }
      });
    }, { threshold: 0.6 });

    observer.observe(video);
  });
});

// --------------------------------busqueda de usuarios--------------------------------

let searchTimeout;

function toggleSearch() {
    const panel = document.getElementById('searchPanel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        document.getElementById('searchInput').focus();
    }
}

document.getElementById('searchInput').addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    const resultsDiv = document.getElementById('searchResults');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (!query) {
        resultsDiv.innerHTML = '';
        return;
    }

    loadingIndicator.classList.remove('hidden');

    searchTimeout = setTimeout(() => {
        fetch(`/buscar_usuarios/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                loadingIndicator.classList.add('hidden');
                resultsDiv.innerHTML = '';

                if (data.usuarios.length === 0) {
                    resultsDiv.innerHTML = `
                        <div class="px-4 py-3 text-sm text-neutral-400">
                            No se encontraron usuarios
                        </div>
                    `;
                    return;
                }

                data.usuarios.forEach(usuario => {
                    const div = document.createElement('div');
                    div.className = 'px-4 py-2 hover:bg-neutral-700 cursor-pointer transition-colors';
                    div.onclick = () => window.location.href = `/perfil/${usuario.username}`;
                    
                    div.innerHTML = `
                        <div class="flex items-center gap-3">
                            <img src="${usuario.imagen_perfil || '/static/myapp/img/perfil_default.jpg'}"
                                alt="${usuario.username}"
                                class="w-11 h-11 rounded-full object-cover">
                            <div>
                                <div class="font-semibold text-white">${usuario.username}</div>
                                <div class="text-sm text-neutral-400">${usuario.nombre_completo}</div>
                                <div class="text-xs text-neutral-500">${usuario.seguidores} seguidores</div>
                            </div>
                        </div>
                    `;
                    resultsDiv.appendChild(div);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                loadingIndicator.classList.add('hidden');
                resultsDiv.innerHTML = `
                    <div class="px-4 py-3 text-sm text-red-400">
                        Error al buscar usuarios
                    </div>
                `;
            });
    }, 300);
});

// Cerrar el panel al hacer clic fuera
document.addEventListener('click', function(e) {
    const panel = document.getElementById('searchPanel');
    const searchButton = document.querySelector('button[onclick="toggleSearch()"]');
    if (!panel.contains(e.target) && !searchButton.contains(e.target)) {
        panel.classList.add('hidden');
    }
});
// ----------------------ocultar nav----------------------

function toggleSearch() {
    const searchPanel = document.getElementById('searchPanel');
    const mainNav = document.getElementById('mainNav');
    const searchInput = document.getElementById('searchInput');
    const navTexts = document.querySelectorAll('nav span:not(.logo-font)');
    const logoText = document.getElementById('logoText');
    const logoIcon = document.getElementById('logoIcon');
    const inicioLink = document.querySelector('a[href="/inicio"]'); // Seleccionar el enlace de inicio

    if (searchPanel.classList.contains('hidden')) {
        // Mostrar panel de búsqueda y colapsar nav
        searchPanel.classList.remove('hidden');
        mainNav.classList.remove('xl:w-[250px]');
        mainNav.classList.add('w-[72px]');
        
        // Ajustar solo el módulo de inicio
        inicioLink.style.marginTop = '2.2rem'; // mt-14 equivalente
        
        // Ocultar textos y cambiar logo
        navTexts.forEach(text => {
            text.style.display = 'none';
        });
        logoText.style.display = 'none';
        logoIcon.style.display = 'block';
        setTimeout(() => searchInput.focus(), 100);
    } else {
        // Ocultar panel de búsqueda y expandir nav
        searchPanel.classList.add('hidden');
        if (window.innerWidth >= 1280) {
            mainNav.classList.add('xl:w-[250px]');
            mainNav.classList.remove('w-[72px]');
            
            // Restaurar margin del módulo de inicio
            inicioLink.style.marginTop = 'mt-3'; // mt-3 original
            
            // Mostrar textos y cambiar logo
            navTexts.forEach(text => {
                text.style.display = '';
            });
            logoText.style.display = '';
            logoIcon.style.display = 'none';
        }
    }
}

// Actualizar el listener de click fuera
document.addEventListener('click', function(e) {
    const searchPanel = document.getElementById('searchPanel');
    const mainNav = document.getElementById('mainNav');
    const searchButton = document.querySelector('[onclick="toggleSearch()"]');
    const navTexts = document.querySelectorAll('nav span:not(.logo-font)');
    const logoText = document.getElementById('logoText');
    const logoIcon = document.getElementById('logoIcon');
    const inicioLink = document.querySelector('a[href="/inicio"]');
    
    if (!searchPanel.contains(e.target) && !searchButton.contains(e.target)) {
        // Ocultar panel de búsqueda
        searchPanel.classList.add('hidden');
        
        // Restaurar el nav a su estado original
        mainNav.classList.add('xl:w-[250px]');
        mainNav.classList.remove('w-[72px]');
        
        // Restaurar margin del módulo de inicio
        inicioLink.style.marginTop = '0.75rem';
        
        // Mostrar todos los textos
        navTexts.forEach(text => {
            text.style.display = '';
        });
        
        // Cambiar el logo
        logoText.style.display = '';
        logoIcon.style.display = 'none';
    }
});


// -----------------------crear_reels-----------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalFormulario');
    const contenidoModal = document.getElementById('contenidoModal');
    const abrirReelBtn = document.getElementById('abrirReel');

    // Abrir modal y cargar el formulario desde la URL
    abrirReelBtn.addEventListener('click', async () => {
        const res = await fetch('/reels/crear/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const html = await res.text();
        contenidoModal.innerHTML = html;

        // Botón de cerrar dinámico
        const cerrarBtn = document.createElement('button');
        cerrarBtn.innerHTML = '&times;';
        cerrarBtn.className = 'absolute top-2 right-2 text-gray-500 hover:text-white text-2xl';
        cerrarBtn.type = 'button';
        cerrarBtn.addEventListener('click', () => modal.classList.add('hidden'));
        contenidoModal.appendChild(cerrarBtn);

        inicializarEnvioFormulario(); // Añadir el listener de envío

        modal.classList.remove('hidden');
    });

    // Cerrar modal si se hace click fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    // Función para manejar el submit del formulario de subida
    function inicializarEnvioFormulario() {
        const form = document.getElementById('formReel');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const res = await fetch('/reels/crear/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (res.ok) {
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Reel subido correctamente');
                    modal.classList.add('hidden');
                    location.reload(); // Recargar los reels
                }
            } else {
                const data = await res.json();
                alert('❌ Errores: ' + JSON.stringify(data.errores));
            }
        });
    }
});