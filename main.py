from identify import identify_species
from db import SessionLocal
from models import Observation
from rag import RAGSystem
import shutil
import os
from datetime import date

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
    date_observed: date = None,
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