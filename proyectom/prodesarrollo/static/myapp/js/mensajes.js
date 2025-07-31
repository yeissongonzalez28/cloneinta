const form = document.getElementById('chat-form');
const mensajeInput = document.getElementById('mensaje');
const receptor = document.getElementById('receptor')?.value;
const chatBox = document.getElementById('chat-box');

form?.addEventListener('submit', function (e) {
    e.preventDefault();

    fetch("{% url 'enviar_mensaje' %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            mensaje: mensajeInput.value,
            receptor: receptor
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado === 'ok') {
            const mensaje = `
                <div class="flex flex-col items-end">
                    <div class="bg-blue-500 text-white rounded-2xl px-4 py-2 max-w-[80%]">
                        ${data.mensaje}
                    </div>
                </div>`;
            chatBox.insertAdjacentHTML('beforeend', mensaje);
            mensajeInput.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    });
});

// Cargar mensajes cada 3 segundos
setInterval(() => {
    if (!receptor) return;
    fetch(`/obtener_mensajes/${receptor}/`)
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML = '';
            data.mensajes.forEach(msg => {
                const isCurrentUser = msg.enviar === '{{ request.user.username }}';
                const mensaje = `
                    <div class="flex flex-col ${isCurrentUser ? 'items-end' : 'items-start'}">
                        <div class="${isCurrentUser ? 'bg-blue-500 text-white' : 'bg-zinc-800 text-white'} rounded-2xl px-4 py-2 max-w-[80%]">
                            ${msg.contenido}
                        </div>
                    </div>`;
                chatBox.innerHTML += mensaje;
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        });
}, 2000);