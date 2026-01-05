// Configuración del Backend
let BACKEND_URL = "http://localhost:5000"; // Valor por defecto para local

// Detectar si estamos en un entorno de "Live Server" o similar (localhost/127.0.0.1)
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

// Si NO es localhost (es decir, estamos desplegados) y no es archivo local (file://),
// asumimos que el backend está en una URL de producción que debes configurar.
// Puedes cambiar 'https://tu-backend-real.com' por tu URL de Railway/Render/etc.
if (!isLocalhost && window.location.protocol !== 'file:') {
    BACKEND_URL = "https://tu-backend-real.com";
    // O si el backend sirve el frontend, podrías usar:
    // BACKEND_URL = window.location.origin;
}

console.log("Conectando a:", BACKEND_URL);

let socket;
let currentUser = "";
let currentRoom = "";

// Elementos del DOM
const loginScreen = document.getElementById('login-screen');
const chatScreen = document.getElementById('chat-screen');
const usernameInput = document.getElementById('username-input');
const roomInput = document.getElementById('room-input');
const joinBtn = document.getElementById('join-btn');
const roomTitle = document.getElementById('room-title');
const messagesContainer = document.getElementById('messages-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const leaveBtn = document.getElementById('leave-btn');

// --- Funciones de Utilidad ---

function addMessageToUI(user, content, timestamp, type = 'normal') {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');

    if (type === 'system' || user === 'Sistema') {
        msgDiv.classList.add('system-message');
        msgDiv.textContent = content;
    } else {
        if (user === currentUser) {
            msgDiv.classList.add('my-message');
        } else {
            msgDiv.classList.add('other-message');
        }

        // Formato simple de fecha/hora
        const date = new Date(timestamp);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        msgDiv.innerHTML = `
            <strong>${user}</strong>: ${content}
            <span class="message-meta">${timeStr}</span>
        `;
    }

    messagesContainer.appendChild(msgDiv);
    // Auto-scroll al final
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// --- Lógica de Conexión y Eventos ---

joinBtn.addEventListener('click', () => {
    const user = usernameInput.value.trim();
    const room = roomInput.value.trim();

    if (!user || !room) {
        alert("Por favor ingresa un usuario y una sala.");
        return;
    }

    currentUser = user;
    currentRoom = room;

    // Conectar al WebSocket
    socket = io(BACKEND_URL);

    socket.on('connect', () => {
        console.log("Conectado al servidor");
        // Emitir evento de 'unirse'
        socket.emit('join', { username: user, room: room });

        // Cambiar pantalla
        loginScreen.classList.add('hidden');
        chatScreen.classList.remove('hidden');
        roomTitle.textContent = `Sala: ${room}`;
    });

    // Recibir historial completo
    socket.on('history', (messages) => {
        messagesContainer.innerHTML = ''; // Limpiar por si acaso
        messages.forEach(msg => {
            addMessageToUI(msg.user, msg.content, msg.timestamp);
        });
    });

    // Recibir mensajes nuevos
    socket.on('message', (data) => {
        addMessageToUI(data.user, data.content, data.timestamp);
    });
});

sendBtn.addEventListener('click', sendMessage);

// Permitir enviar con Enter
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const text = messageInput.value.trim();
    if (text && socket) {
        // Emitir mensaje
        socket.emit('message', {
            username: currentUser,
            room: currentRoom,
            content: text
        });
        messageInput.value = '';
        // Nota: No agregamos el mensaje a la UI aquí manualmente,
        // esperamos a que el servidor nos lo "re-broadcast" (envíe de vuelta)
        // para asegurar consistencia, o lo agregamos si se prefiere feedback instantáneo.
        // En este caso, app.py hace broadcast a la sala, así que nos llegará por 'message'.
    }
}

leaveBtn.addEventListener('click', () => {
    if (socket) {
        socket.disconnect();
    }
    // Resetear UI
    loginScreen.classList.remove('hidden');
    chatScreen.classList.add('hidden');
    messagesContainer.innerHTML = '';
    currentUser = "";
    currentRoom = "";
});
