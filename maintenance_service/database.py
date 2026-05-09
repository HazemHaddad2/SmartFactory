from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL - connexion vers le PostgreSQL local via Docker
DATABASE_URL = "postgresql://postgres:admin1234@host.docker.internal:5432/smartfactory_maintenance"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "client_encoding": "utf8",
        "application_name": "smartfactory_maintenance_service"
    },
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
