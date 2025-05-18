from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from identify import identify_species
from db import SessionLocal, init_db
from models import Observation
from sightings_manager import SightingsManager
from rag import RAGSystem
import shutil
import os
from datetime import date, datetime

app = FastAPI()

# Initialize the database
init_db()

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize SightingsManager and RAGSystem
sightings_manager = SightingsManager()
rag_system = RAGSystem()

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

        suggestions = await identify_species(file_path, lat, lng)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            image.file.close()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up file {file_path}: {str(e)}")

@app.post("/observations/")
async def add_observation(
    species_name: str = Form(...),
    common_name: str = Form(""),
    date_observed: date = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_description: str = Form(""),
    notes: str = Form(""),
    image: UploadFile = File(None)
):
    try:
        if image:
            result = await sightings_manager.save_sighting(
                species_name=species_name,
                common_name=common_name,
                latitude=latitude,
                longitude=longitude,
                location_description=location_description,
                notes=notes,
                image_file=image,
                date_observed=date_observed
            )
            if not result:
                raise HTTPException(status_code=500, detail="Failed to save sighting")
        else:
            # Save observation without image
            session = SessionLocal()
            try:
                species_type = await sightings_manager._determine_species_type(species_name.lower(), common_name.lower())
                obs = Observation(
                    species_name=species_name,
                    common_name=common_name,
                    date_observed=date_observed,
                    latitude=latitude,
                    longitude=longitude,
                    location_description=location_description,
                    notes=notes,
                    species_type=species_type
                )
                session.add(obs)
                session.commit()
            finally:
                session.close()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/observations/")
async def get_observations():
    """Get all observations from the database."""
    session = SessionLocal()
    try:
        observations = session.query(Observation).order_by(Observation.date_observed.desc()).all()
        return [
            {
                "species_name": obs.species_name,
                "common_name": obs.common_name,
                "latitude": obs.latitude,
                "longitude": obs.longitude,
                "location_description": obs.location_description,
                "notes": obs.notes,
                "image_url": obs.image_url,
                "date": obs.date_observed.isoformat(),
                "type": obs.species_type,
                "timestamp": obs.date_observed.isoformat()
            }
            for obs in observations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/recent-sightings/{species_type}")
async def get_recent_sightings(species_type: str, limit: int = 5):
    """Get recent sightings for birds, mammals, plants, amphibians, reptiles, insects, or other."""
    try:
        if species_type not in ["birds", "mammals", "plants", "amphibians", "reptiles", "insects", "other"]:
            raise HTTPException(status_code=400, detail="Invalid species type")
        
        return sightings_manager.get_recent_sightings(species_type, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """Ask a question about local biodiversity."""
    try:
        result = rag_system.ask_question(question)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
