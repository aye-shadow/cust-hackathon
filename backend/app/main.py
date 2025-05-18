from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import date
from pathlib import Path
import os
import json
from PIL import Image
import io
import shutil

app = FastAPI(title="BioScout API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up base paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = BASE_DIR / "data"
SIGHTINGS_DIR = DATA_DIR / "sightings"
IMAGES_DIR = SIGHTINGS_DIR / "images"

# Ensure directories exist
SIGHTINGS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to BioScout API"}

@app.get("/recent-sightings/{species_type}")
async def get_recent_sightings(species_type: str):
    try:
        # Read from the appropriate CSV file
        sightings_file = SIGHTINGS_DIR / f"{species_type}.csv"
        if not sightings_file.exists():
            return []
        
        # Read and parse CSV file
        # Add your existing CSV reading logic here
        sightings = []  # Replace with actual CSV reading
        return sightings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/identify/")
async def identify_species(
    image: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...)
):
    try:
        # Your existing species identification logic here
        # Return mock data for now
        suggestions = [
            {"name": "Sample Species", "rank": "Common", "confidence": 95.5}
        ]
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/observations/")
async def create_observation(
    image: UploadFile = File(...),
    species_name: str = Form(...),
    common_name: str = Form(...),
    date_observed: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_description: str = Form(None),
    notes: str = Form(None)
):
    try:
        # Save image
        image_path = IMAGES_DIR / f"{date_observed}_{species_name.replace(' ', '_')}.jpg"
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Save observation data
        # Add your existing CSV writing logic here
        
        return {"message": "Observation saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        # Your existing Q&A logic here
        # Return mock data for now
        return {
            "answer": "This is a sample answer.",
            "sources": [{"text": "Sample source text"}]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 