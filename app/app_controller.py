from sqlalchemy import Date
import os
import shutil
from rag import RAGSystem
from inaturalist_api import identify_species
from models import Observation, SessionLocal
from sightings_manager import SightingsManager
from datetime import date

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Instantiate singletons at module level
_rag_system = None
_sightings_manager = SightingsManager()

def get_rag_system():
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system

def get_sightings_manager():
    return _sightings_manager

def identify(image_file, lat: float, lng: float):
    """Identify species from an image file and coordinates."""
    file_path = None
    try:
        file_path = f"temp/{image_file.name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file, buffer)

        suggestions = identify_species(file_path, lat, lng)
        return suggestions
    except Exception as e:
        raise RuntimeError(str(e))
    finally:
        try:
            image_file.close()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up file {file_path}: {str(e)}")

def ask_question(question: str):
    """Ask a question about local biodiversity."""
    try:
        print(f"Received question: {question}")  # Debug print
        result = get_rag_system().ask_question(question)
        print(f"Got result: {result}")  # Debug print

        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"]
            print(f"Error from RAG system: {error_msg}")  # Debug print
            raise RuntimeError(error_msg)
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Error processing question: {str(e)}\nTrace:\n{error_trace}"
        print(error_msg)  # Debug print
        raise RuntimeError(error_msg)

async def add_observation(
    species_name: str,
    common_name: str = "",
    date_observed: date = None,
    latitude: float = None,
    longitude: float = None,
    notes: str = "",
    image_file=None,
):
    """Add a new observation to the database and optionally save a sighting with image."""
    try:
        session = SessionLocal()
        try:
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
        finally:
            session.close()

        if image_file:
            if hasattr(image_file, "seek"):
                image_file.seek(0)
            result = await get_sightings_manager().save_sighting(
                species_name=species_name,
                common_name=common_name,
                latitude=latitude,
                longitude=longitude,
                notes=notes,
                image_file=image_file,
                location_description=f"Coordinates: {latitude}, {longitude}"
            )
            if not result:
                raise RuntimeError("Failed to save sighting")

        return {"status": "success"}
    except Exception as e:
        raise RuntimeError(str(e))

def get_observations():
    """Get all observations from the database."""
    session = SessionLocal()
    try:
        data = session.query(Observation).all()
        return data
    except Exception as e:
        raise RuntimeError(str(e))
    finally:
        session.close()

def get_recent_sightings(species_type: str, limit: int = 5):
    """Get recent sightings for birds, mammals, plants, or other."""
    try:
        if species_type not in ["birds", "mammals", "plants", "other"]:
            raise ValueError("Invalid species type")
        sightings = get_sightings_manager().get_recent_sightings(species_type, limit)
        return sightings
    except Exception as e:
        raise RuntimeError(str(e))