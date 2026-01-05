from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlmodel import Session, select
from database import engine, init_db, get_session, production_engine
from models import User, Room, Message
import datetime

# Inicialización de Flask y Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# CORS permitido para todo origen para facilitar pruebas locales independientes
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Eventos de WebSocket ---

@socketio.on('connect')
def handle_connect():
    """Se ejecuta cuando un cliente se conecta al WebSocket."""
    print(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Se ejecuta cuando un cliente se desconecta."""
    print(f"Cliente desconectado: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """
    Maneja la unión de un usuario a una sala.
    Data esperada: {'username': 'nombre', 'room': 'sala'}
    """
    username = data['username']
    room_name = data['room']

    print(f"Usuario {username} entrando a sala {room_name}")

    with Session(production_engine) as session:
        # 1. Buscar o crear Usuario
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.commit()
            session.refresh(user)

        # 2. Buscar o crear Sala
        room = session.exec(select(Room).where(Room.name == room_name)).first()
        if not room:
            room = Room(name=room_name)
            session.add(room)
            session.commit()
            session.refresh(room)

        # Unir al cliente a la sala de SocketIO
        join_room(room_name)

        # 3. Recuperar TODO el historial de mensajes de la sala
        # Ordenados por fecha
        messages = session.exec(select(Message).where(Message.room_id == room.id).order_by(Message.timestamp)).all()
        
        history = [msg.to_dict() for msg in messages]

        # Enviar historial SOLO al usuario que acaba de entrar
        emit('history', history, to=request.sid)

        # Notificar a los demás en la sala
        emit('message', {
            'user': 'Sistema',
            'content': f'{username} se ha unido a la sala.',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name)

@socketio.on('message')
def handle_message(data):
    """
    Maneja el envío de mensajes.
    Data esperada: {'username': 'nombre', 'room': 'sala', 'content': 'hola'}
    """
    username = data['username']
    room_name = data['room']
    content = data['content']

    with Session(production_engine) as session:
        # Buscamos ids (asumimos que existen porque se unió antes)
        user = session.exec(select(User).where(User.username == username)).first()
        room = session.exec(select(Room).where(Room.name == room_name)).first()
        
        if user and room:
            # Guardar mensaje en BD
            new_msg = Message(content=content, user_id=user.id, room_id=room.id)
            session.add(new_msg)
            session.commit()
            session.refresh(new_msg)
            
            # Reenviar a todos en la sala (incluyendo al remitente para confirmación visual inmediata)
            # Ojo: A veces se prefiere 'broadcast=True' o 'include_self=True' (default)
            emit('message', new_msg.to_dict(), room=room_name)

if __name__ == '__main__':
    # Inicializar la base de datos al arrancar
    init_db()
    # Ejecutar la app con SocketIO
    print("Iniciando servidor en http://127.0.0.1:5000")
    socketio.run(app, debug=True, port=5000)
