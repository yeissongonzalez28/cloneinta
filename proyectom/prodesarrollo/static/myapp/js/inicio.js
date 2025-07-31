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
                            <img src="${usuario.avatar}"
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





// ------------------------recortedepublicacion-------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  const inputFile = document.getElementById('file-upload');
  const modalRecorte = document.getElementById('modalRecorte');
  const imagenRecorte = document.getElementById('imagenRecorte');
  const selector = document.getElementById('selectorRecorte');
  const btnRecortar = document.getElementById('btnRecortar');
  const cancelarRecorte = document.getElementById('cancelarRecorte');

  const btnAspect45 = document.getElementById('btnAspect45');
  const btnAspect169 = document.getElementById('btnAspect169');
  const aspectInput = document.getElementById('aspect_ratio');

  const preview = document.getElementById('previewPublicacion');
  const previewContainer = document.getElementById('preview-container');
  const uploadText = document.getElementById('uploadTextPublicacion');

  let img = new Image();
  let fileOriginal;
  let isDragging = false, isResizing = false;
  let startX, startY, startW, startH;

  // proporción por defecto
  let currentAspect = 4 / 5;

  // Al seleccionar el archivo
  inputFile.addEventListener('change', (e) => {
    fileOriginal = e.target.files[0];

    if (fileOriginal) {
      // Si es imagen → abrir modal de recorte
      if (fileOriginal.type.startsWith('image/')) {
        img.src = URL.createObjectURL(fileOriginal);
        imagenRecorte.src = img.src;
        modalRecorte.classList.remove('hidden');

        imagenRecorte.onload = () => inicializarMarco();
      }

      // Si es video → no recortamos, solo mostramos en preview
      else if (fileOriginal.type.startsWith('video/')) {
        const url = URL.createObjectURL(fileOriginal);

        previewContainer.innerHTML = `
          <div class="w-full h-full">
            <video src="${url}" class="w-full h-full object-cover rounded-lg" autoplay loop muted playsinline></video>
          </div>`;
        uploadText.classList.add('hidden');
        preview.classList.remove('hidden');
      }
    }
  });

  // Inicializar marco de recorte
  function inicializarMarco() {
    const imgRect = imagenRecorte.getBoundingClientRect();
    const cont = imagenRecorte.parentElement;

    let ancho = imgRect.width * 0.8;
    let alto = ancho / currentAspect;

    if (alto > imgRect.height) {
      alto = imgRect.height * 0.8;
      ancho = alto * currentAspect;
    }

    selector.style.width = `${ancho}px`;
    selector.style.height = `${alto}px`;

    const offsetLeft = imgRect.left - cont.getBoundingClientRect().left;
    const offsetTop = imgRect.top - cont.getBoundingClientRect().top;

    selector.style.left = `${offsetLeft + (imgRect.width - ancho) / 2}px`;
    selector.style.top = `${offsetTop + (imgRect.height - alto) / 2}px`;
  }

  // Botones de proporción
  btnAspect45.addEventListener('click', (e) => {
    e.preventDefault();
    currentAspect = 4 / 5;
    aspectInput.value = '4:5';
    btnAspect45.classList.replace('bg-gray-600', 'bg-blue-600');
    btnAspect169.classList.replace('bg-blue-600', 'bg-gray-600');
    inicializarMarco();
  });

  btnAspect169.addEventListener('click', (e) => {
    e.preventDefault();
    currentAspect = 16 / 9;
    aspectInput.value = '16:9';
    btnAspect169.classList.replace('bg-gray-600', 'bg-blue-600');
    btnAspect45.classList.replace('bg-blue-600', 'bg-gray-600');
    inicializarMarco();
  });

  // Mover y redimensionar
  selector.addEventListener('mousedown', (e) => {
    if (e.target.classList.contains('handle')) {
      isResizing = true;
      startX = e.clientX;
      startY = e.clientY;
      startW = selector.offsetWidth;
      startH = selector.offsetHeight;
    } else {
      isDragging = true;
      startX = e.clientX - selector.offsetLeft;
      startY = e.clientY - selector.offsetTop;
    }
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    isResizing = false;
  });

  document.addEventListener('mousemove', (e) => {
    const cont = imagenRecorte.parentElement;

    if (isDragging) {
      let x = e.clientX - startX;
      let y = e.clientY - startY;

      x = Math.max(0, Math.min(x, cont.clientWidth - selector.clientWidth));
      y = Math.max(0, Math.min(y, cont.clientHeight - selector.clientHeight));

      selector.style.left = `${x}px`;
      selector.style.top = `${y}px`;
    }

    if (isResizing) {
      let diffX = e.clientX - startX;
      let newW = startW + diffX;
      let newH = newW / currentAspect;

      if (newW < 50) {
        newW = 50;
        newH = newW / currentAspect;
      }

      if (newW > cont.clientWidth) {
        newW = cont.clientWidth;
        newH = newW / currentAspect;
      }
      if (newH > cont.clientHeight) {
        newH = cont.clientHeight;
        newW = newH * currentAspect;
      }

      selector.style.width = `${newW}px`;
      selector.style.height = `${newH}px`;
    }
  });

  // Recortar imagen
  btnRecortar.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const imgRect = imagenRecorte.getBoundingClientRect();
    const selRect = selector.getBoundingClientRect();

    const sx = (selRect.left - imgRect.left) * (img.width / imgRect.width);
    const sy = (selRect.top - imgRect.top) * (img.height / imgRect.height);
    const sw = selRect.width * (img.width / imgRect.width);
    const sh = selRect.height * (img.height / imgRect.height);

    let outW = 1080;
    let outH = Math.round(outW / currentAspect);

    canvas.width = outW;
    canvas.height = outH;

    ctx.drawImage(img, sx, sy, sw, sh, 0, 0, outW, outH);

    const dataURL = canvas.toDataURL('image/jpeg');
    canvas.toBlob((blob) => {
      const fileRecortado = new File([blob], fileOriginal.name, { type: 'image/jpeg' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(fileRecortado);
      inputFile.files = dataTransfer.files;

      // Mostrar preview final
      previewContainer.innerHTML = `
        <div class="w-full h-full">
          <img src="${dataURL}" class="w-full h-full object-cover rounded-lg">
        </div>`;
      uploadText.classList.add('hidden');
      preview.classList.remove('hidden');

      modalRecorte.classList.add('hidden');
    });
  });

  cancelarRecorte.addEventListener('click', () => {
    modalRecorte.classList.add('hidden');
  });

  // Cancelar modal de publicación
  const modalPublicacion = document.getElementById('modalPublicacion');
  const cancelarModalPublicacion = document.getElementById('cancelarModalPublicacion');

  cancelarModalPublicacion.addEventListener('click', () => {
    modalPublicacion.classList.add('hidden');

    // Limpia vista previa y file input
    inputFile.value = '';
    previewContainer.innerHTML = '';
    preview.classList.add('hidden');
    uploadText.classList.remove('hidden');
  });
});
