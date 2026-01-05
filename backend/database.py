from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# Configuración MySQL (producción)
# =========================
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

production_engine = create_engine(DATABASE_URL, echo=True)

# =========================
# Configuración SQLite (desarrollo local)
# =========================
sqlite_url = "sqlite:///chat.db"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    echo=True
)

# =========================
# Inicialización BD
# =========================
def init_db():
    """Crea las tablas en la base de datos si no existen."""
    SQLModel.metadata.create_all(production_engine)

def get_session():
    """Obtiene una sesión de base de datos."""
    with Session(production_engine) as session:
        yield session
