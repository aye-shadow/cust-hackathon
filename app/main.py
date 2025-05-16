from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import shutil
from rag import RAGSystem
from identify import identify_species

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
if not SUPABASE_DB_URL:
    raise RuntimeError("SUPABASE_DB_URL environment variable not set. Please check your .env file.")

engine = create_engine(SUPABASE_DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define your ORM model
class Observation(Base):
    __tablename__ = "observations"
    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String, nullable=False)
    common_name = Column(String, default="")
    date_observed = Column(Date)
    latitude = Column(Float)
    longitude = Column(Float)
    notes = Column(Text, default="")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize RAG system
rag_system = RAGSystem()

def identify(image_file, lat: float, lng: float):
    """Identify species from an image file and coordinates."""
    try:
        file_path = f"temp/{image_file.name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file, buffer)

        suggestions = identify_species(file_path, lat, lng)
        
        # Clean up the temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return suggestions
    except Exception as e:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise RuntimeError(str(e))

def ask_question(question: str):
    """Ask a question about local biodiversity."""
    try:
        result = rag_system.ask_question(question)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])
        return result
    except Exception as e:
        raise RuntimeError(f"Error processing question: {str(e)}")

def add_observation(
    species_name: str,
    common_name: str = "",
    date_observed: Date = None,
    latitude: float = None,
    longitude: float = None,
    notes: str = "",
):
    """Add a new observation to the database."""
    session = SessionLocal()
    obs = Observation(
        species_name=species_name,
        common_name=common_name,
        date_observed=date_observed,
        latitude=latitude,
        longitude=longitude,
        notes=notes
    )
    session.add(obs)
    session.commit()
    session.close()
    return {"status": "success"}

def get_observations():
    """Get all observations from the database."""
    session = SessionLocal()
    data = session.query(Observation).all()
    session.close()
    return data