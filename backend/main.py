from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from identify import identify_species
from db import SessionLocal
from models import Observation
from rag import RAGSystem
from sightings_manager import SightingsManager
import shutil
import os
from datetime import date, datetime

app = FastAPI()

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize RAG system and SightingsManager
rag_system = RAGSystem()
sightings_manager = SightingsManager()

# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sightings")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/identify/")
async def identify(image: UploadFile = File(...), lat: float = Form(...), lng: float = Form(...)):
    file_path = None
    try:
        file_path = f"temp/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        suggestions = identify_species(file_path, lat, lng)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up: ensure file handle is closed and file is deleted
        try:
            image.file.close()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up file {file_path}: {str(e)}")

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """Endpoint for asking questions about local biodiversity."""
    try:
        print(f"Received question: {question}")  # Debug print
        result = rag_system.ask_question(question)
        print(f"Got result: {result}")  # Debug print
        
        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"]
            print(f"Error from RAG system: {error_msg}")  # Debug print
            raise HTTPException(status_code=500, detail=error_msg)
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = f"Error processing question: {str(e)}\nTrace:\n{error_trace}"
        print(error_msg)  # Debug print
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/observations/")
async def add_observation(
    species_name: str = Form(...),
    common_name: str = Form(""),
    date_observed: date = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    notes: str = Form(""),
    image: UploadFile = File(None)
):
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

        # Save to sightings system
        if image:
            result = await sightings_manager.save_sighting(
                species_name=species_name,
                common_name=common_name,
                latitude=latitude,
                longitude=longitude,
                notes=notes,
                image_file=image,
                location_description=f"Coordinates: {latitude}, {longitude}"
            )
            if not result:
                raise HTTPException(status_code=500, detail="Failed to save sighting")

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/observations/")
def get_observations():
    session = SessionLocal()
    try:
        data = session.query(Observation).all()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/recent-sightings/{species_type}")
def get_recent_sightings(species_type: str, limit: int = 5):
    """Get recent sightings for birds, mammals, plants, amphibians, reptiles, insects, or other."""
    try:
        if species_type not in ["birds", "mammals", "plants", "amphibians", "reptiles", "insects", "other"]:
            raise HTTPException(status_code=400, detail="Invalid species type")
        
        sightings = sightings_manager.get_recent_sightings(species_type, limit)
        return sightings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
