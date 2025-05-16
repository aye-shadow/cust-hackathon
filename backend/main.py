from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from identify import identify_species
from db import SessionLocal
from models import Observation
from rag import RAGSystem
import shutil
import os
from datetime import date

app = FastAPI()

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize RAG system
rag_system = RAGSystem()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/identify/")
async def identify(image: UploadFile = File(...), lat: float = Form(...), lng: float = Form(...)):
    try:
        file_path = f"temp/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        suggestions = identify_species(file_path, lat, lng)
        
        # Clean up the temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return suggestions
    except Exception as e:
        # Clean up the temp file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

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
):
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

@app.get("/observations/")
def get_observations():
    session = SessionLocal()
    data = session.query(Observation).all()
    session.close()
    return data
