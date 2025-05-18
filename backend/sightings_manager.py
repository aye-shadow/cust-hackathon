import os
import shutil
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import UploadFile
from langchain_groq import ChatGroq
from db import SessionLocal
from models import Observation

class SightingsManager:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sightings")
        self.images_dir = os.path.join(self.base_dir, "images")
        
        # Initialize Groq for species classification
        os.environ["GROQ_API_KEY"] = "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"
        
        self.llm = ChatGroq(
            model_name="llama3-8b-8192",
            temperature=0.1,
            max_tokens=100
        )
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)

    async def _determine_species_type(self, species_name: str, common_name: str) -> str:
        """Use Groq to determine if the species is a bird, mammal, plant, amphibian, reptile, insect, or other."""
        print(f"Determining species type for: {species_name} ({common_name})")

        prompt = f"""As a biodiversity expert, classify the following species into one of these categories: birds, mammals, plants, amphibians, reptiles, insects, or other.
        Species Name: {species_name}
        Common Name: {common_name}

        Consider the following:
        - Birds are feathered vertebrates that lay eggs
        - Mammals are warm-blooded vertebrates that typically give birth to live young
        - Plants are photosynthetic organisms that typically don't move
        - Amphibians are cold-blooded vertebrates that typically start life in water and metamorphose
        - Reptiles are cold-blooded vertebrates with scales that typically lay eggs
        - Insects are arthropods with six legs and three body segments
        - Use 'other' for fungi, fish, arachnids (except when grouped with insects), etc.

        Respond with ONLY ONE of these exact words: birds, mammals, plants, amphibians, reptiles, insects, other"""

        try:
            response = await self.llm.ainvoke(prompt)
            classification = response.content.lower().strip()
            print(f"Groq classified {species_name} as: {classification}")

            valid_categories = {"birds", "mammals", "plants", "amphibians", "reptiles", "insects", "other"}
            if classification not in valid_categories:
                print(f"Invalid classification from Groq: {classification}, defaulting to 'other'")
                return "other"
            
            return classification
        except Exception as e:
            print(f"Error in Groq classification: {str(e)}, defaulting to 'other'")
            return "other"

    async def save_sighting(
        self,
        species_name: str,
        common_name: str,
        latitude: float,
        longitude: float,
        location_description: str,
        notes: str,
        image_file: UploadFile,
        date_observed: datetime
    ) -> bool:
        """Save a new sighting with image and metadata to the database."""
        try:
            # Determine species type
            species_type = await self._determine_species_type(species_name.lower(), common_name.lower())
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{species_type}_{timestamp}.jpg"
            image_path = os.path.join(self.images_dir, image_filename)
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            
            # Save to database
            session = SessionLocal()
            try:
                observation = Observation(
                    species_name=species_name,
                    common_name=common_name,
                    date_observed=date_observed,
                    latitude=latitude,
                    longitude=longitude,
                    location_description=location_description,
                    notes=notes,
                    image_url=f"/static/images/{image_filename}",
                    species_type=species_type
                )
                session.add(observation)
                session.commit()
                return True
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error saving sighting: {str(e)}")
            return False

    def get_recent_sightings(self, species_type: str, limit: int = 5) -> List[Dict]:
        """Get recent sightings for a specific species type from the database."""
        try:
            session = SessionLocal()
            try:
                sightings = (
                    session.query(Observation)
                    .filter(Observation.species_type == species_type)
                    .order_by(Observation.date_observed.desc())
                    .limit(limit)
                    .all()
                )
                
                return [
                    {
                        "species_name": s.species_name,
                        "common_name": s.common_name,
                        "latitude": s.latitude,
                        "longitude": s.longitude,
                        "location_description": s.location_description,
                        "notes": s.notes,
                        "image_url": s.image_url,
                        "date": s.date_observed.isoformat(),
                        "type": s.species_type
                    }
                    for s in sightings
                ]
            finally:
                session.close()
        except Exception as e:
            print(f"Error getting sightings: {str(e)}")
            return []

    def cleanup(self) -> None:
        """Remove all sightings data (images and database records)."""
        try:
            # Remove all files in images directory
            for filename in os.listdir(self.images_dir):
                file_path = os.path.join(self.images_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Remove all database records
            session = SessionLocal()
            try:
                session.query(Observation).delete()
                session.commit()
            finally:
                session.close()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}") 