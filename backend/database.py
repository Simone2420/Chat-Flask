from sqlmodel import SQLModel, create_engine, Session

# Usamos SQLite para simplificar. 
# "check_same_thread=False" es necesario para SQLite con multithreading en Flask.
sqlite_file_name = "chat.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    """Crea las tablas en la base de datos si no existen."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Helper para obtener una sesión de base de datos."""
    with Session(engine) as session:
        yield session
