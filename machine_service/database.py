from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL - connexion vers le PostgreSQL local via Docker
DATABASE_URL = "postgresql://postgres:admin1234@host.docker.internal:5432/smartfactory_machines"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
