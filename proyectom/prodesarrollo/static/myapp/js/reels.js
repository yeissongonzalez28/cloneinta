// mostrar reels y sus funciones

document.addEventListener('DOMContentLoaded', async () => {
const container = document.getElementById('reels-container');
let page = 1;
let hasNext = true;


function getCSRF() {
    return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

// pausar el resto
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
    const video = entry.target.querySelector('video');
    if (!video) return;

    if (entry.isIntersecting && entry.intersectionRatio > 0.7) {
        video.play().catch(() => {});
    } else {
        video.pause();
    }
    });
}, { threshold: [0.7] });

// Inicializa botón Like
function inicializarLike(btn) {
    btn.addEventListener('click', async () => {
    const svg = btn.querySelector('svg');
    const path = svg.querySelector('path');
    const reelId = btn.dataset.id;

    const res = await fetch(`/reels/${reelId}/like/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF() }
    });
    const data = await res.json();

    btn.querySelector('div').textContent = data.likes;

    if (data.likeado) {
        svg.classList.add('scale-125');
        path.setAttribute('fill', '#ff3040');
        path.setAttribute('stroke', '#ff3040');
    } else {
        svg.classList.remove('scale-125');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', 'white');
    }
    });
}

// Inicializa botón sonido
function inicializarSonido(btn) {
    btn.addEventListener('click', () => {
    const video = btn.closest('section').querySelector('video');
    video.muted = !video.muted;
    btn.textContent = video.muted ? '🔇' : '🔊';
    });
}

// Inicializa video (pausa al click + loop)
function inicializarVideo(video) {
    // Toggle play/pause al hacer click en el video
    video.addEventListener('click', () => {
    if (video.paused) {
        video.play();
    } else {
        video.pause();
    }
    });

    // Repetir automáticamente al finalizar
    video.addEventListener('ended', () => {
    video.currentTime = 0;
    video.play();
    });
}

// Render de cada Reel
function addReel(reel) {
    const template = `
    <section class="h-screen snap-start relative flex items-center justify-center">
        <div class="relative h-full max-h-[100%] w-auto mb-10">
        <video class="h-full max-h-[90%] w-auto mb-10"
        src="${reel.video_url}" playsinline muted preload="metadata"></video>
        
        <button class="absolute top-6 right-1 bg-black/40 px-2 py-2 rounded text-sm toggle-sound">🔇</button>

        <div class="absolute left-3 bottom-6 right-24 mb-[19%]">
            <div class="flex items-center gap-2 mb-2">
            <img src="${reel.autor_imagen}" alt="Autor" class="w-8 h-8 object-cover">
            <div class="flex font-bold items-center">${reel.autor_username}</div>
            </div>
            <div class="text-sm text-white font-bold opacity-80">${reel.titulo}</div>
            <div class="text-xs opacity-60 mt-1">♪ ${reel.audio}</div>
        </div>
        </div>
        <div class="absolute ml-[40%] mb-[10%] bottom-28 flex flex-col gap-6 items-center">
        <button class="like-btn flex flex-col items-center ml-[10%]" data-id="${reel.id}">
            <svg class="heart-anim w-8 h-8 transition transform duration-300 ease-in-out ${reel.ya_likeado ? 'scale-125' : ''}" viewBox="0 0 24 24">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5
                C2 6 4 4 6.5 4c1.74 0 3.41 1 4.5 2.09
                C12.09 5 13.76 4 15.5 4C18 4 20 6 20 9.1
                c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                fill="${reel.ya_likeado ? '#ff3040' : 'none'}"
                stroke="${reel.ya_likeado ? '#ff3040' : 'white'}"
                stroke-width="2" />
            </svg>
            <div class="text-sm text-center">${reel.likes}</div>
        </button>

            <a href="#" class="comment-btn">
            <svg class="w-8 h-8 text-white transition transform duration-300 hover:scale-125"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 11.5c0 4.694-4.253 8.5-9.5 8.5
                -1.15 0-2.255-.198-3.27-.563L3 21l1.706-4.405
                C3.641 15.125 3 13.376 3 11.5
                3 6.806 7.253 3 12.5 3S21 6.806 21 11.5z"
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            </a>
            </div>
    </section>
    `;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = template.trim();
    const section = wrapper.firstChild;

    // Inicializar funciones
    inicializarLike(section.querySelector('.like-btn'));
    inicializarSonido(section.querySelector('.toggle-sound'));
    inicializarVideo(section.querySelector('video'));

    container.appendChild(section);
    observer.observe(section);
}

// Cargar reels
async function cargarReels() {
    const res = await fetch(`/reels/?page=${page}`, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await res.json();
    hasNext = data.has_next;
    data.items.forEach(addReel);
}

await cargarReels();

// Scroll infinito
container.addEventListener('scroll', async () => {
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 200) {
    if (hasNext) {
        page++;
        await cargarReels();
    }
    }
});
});







