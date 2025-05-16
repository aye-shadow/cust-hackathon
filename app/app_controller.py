from sqlalchemy import Date
import os
import shutil
from rag import RAGSystem
from inaturalist_api import identify_species
from models import Observation, SessionLocal
from sightings_manager import SightingsManager

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize RAG system and SightingsManager
rag_system = RAGSystem()
sightings_manager = SightingsManager()

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
        # Clean up: ensure file handle is closed and file is deleted
        try:
            image_file.close()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up file {file_path}: {str(e)}")

def ask_question(question: str):
    """Ask a question about local biodiversity."""
    try:
        result = rag_system.ask_question(question)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Error processing question: {str(e)}\nTrace:\n{error_trace}"
        print(error_msg)
        raise RuntimeError(error_msg)

def add_observation(
    species_name: str,
    common_name: str = "",
    date_observed: Date = None,
    latitude: float = None,
    longitude: float = None,
    notes: str = "",
    image_file=None,
):
    """Add a new observation to the database and optionally save a sighting with image."""
    try:
        # Save to database
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

        # Save to sightings system if image is provided
        if image_file:
            result = sightings_manager.save_sighting(
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
        sightings = sightings_manager.get_recent_sightings(species_type, limit)
        return sightings
    except Exception as e:
        raise RuntimeError(str(e))