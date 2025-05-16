from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
if not SUPABASE_DB_URL:
    raise RuntimeError("SUPABASE_DB_URL environment variable not set. Please check your .env file.")

engine = create_engine(SUPABASE_DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Observation(Base):
    __tablename__ = "observations"
    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String, nullable=False)
    common_name = Column(String, default="")
    date_observed = Column(Date)
    latitude = Column(Float)
    longitude = Column(Float)
    notes = Column(Text, default="")

Base.metadata.create_all(bind=engine)