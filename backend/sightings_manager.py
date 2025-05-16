import os
import csv
from datetime import datetime
from typing import Dict, Optional
import shutil
from langchain_groq import ChatGroq
import re
from rag import RAGSystem

class SightingsManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sightings_dir = os.path.join(self.base_dir, "data", "sightings")
        self.images_dir = os.path.join(self.sightings_dir, "images")
        self.knowledge_dir = os.path.join(self.base_dir, "data")
        
        # Initialize Groq
        os.environ["GROQ_API_KEY"] = "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"
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        self.llm = ChatGroq(
            model_name="llama3-8b-8192",
            temperature=0.1,
            max_tokens=100
        )
        
        # Initialize RAG system
        self.rag_system = RAGSystem()
        
        # Create directories if they don't exist
        os.makedirs(self.sightings_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Initialize CSV files if they don't exist
        self._init_csv("birds.csv")
        self._init_csv("mammals.csv")
        self._init_csv("plants.csv")
        self._init_csv("other.csv")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove spaces and special characters."""
        # Get the name and extension
        name, ext = os.path.splitext(filename)
        
        # Replace spaces and special characters with underscores
        name = re.sub(r'[^\w\-_.]', '_', name)
        name = re.sub(r'\s+', '_', name)
        
        # Remove multiple consecutive underscores
        name = re.sub(r'_+', '_', name)
        
        # Combine name and extension
        return f"{name}{ext.lower()}"

    def _init_csv(self, filename: str):
        """Initialize CSV file with headers if it doesn't exist."""
        filepath = os.path.join(self.sightings_dir, filename)
        if not os.path.exists(filepath):
            headers = ["date", "species_name", "common_name", "latitude", 
                      "longitude", "location_description", "notes", "image_path"]
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    async def _determine_species_type(self, species_name: str, common_name: str) -> str:
        """Use Groq to determine if the species is a bird, mammal, plant, or other."""
        print(f"Determining species type for: {species_name} ({common_name})")

        prompt = f"""As a biodiversity expert, classify the following species into one of these categories: birds, mammals, plants, or other.
        Species Name: {species_name}
        Common Name: {common_name}

        Consider the following:
        - Birds are feathered vertebrates that lay eggs
        - Mammals are warm-blooded vertebrates that typically give birth to live young
        - Plants are photosynthetic organisms that typically don't move
        - Use 'other' for insects, reptiles, amphibians, fish, fungi, etc.

        Respond with ONLY ONE of these exact words: birds, mammals, plants, other"""

        try:
            # Pass the prompt directly as a string
            response = await self.llm.ainvoke(prompt)
            classification = response.content.lower().strip()
            print(f"Groq classified {species_name} as: {classification}")

            # Ensure we get a valid category
            valid_categories = {"birds", "mammals", "plants", "other"}
            if classification not in valid_categories:
                print(f"Invalid classification from Groq: {classification}, defaulting to 'other'")
                return "other"
            
            return classification
        except Exception as e:
            print(f"Error in Groq classification: {str(e)}, defaulting to 'other'")
            return "other"

    async def save_sighting(self, 
                    species_name: str,
                    common_name: str,
                    latitude: float,
                    longitude: float,
                    notes: str,
                    image_file: Optional[Dict] = None,
                    location_description: str = "") -> bool:
        """Save a new sighting to CSV and update knowledge base."""
        try:
            print(f"Saving sighting for: {species_name}")
            
            # Determine species type using Groq
            species_type = await self._determine_species_type(species_name, common_name)
            print(f"Species type determined as: {species_type}")
            
            # Save image if provided
            image_path = ""
            if image_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Sanitize the filename
                sanitized_filename = self._sanitize_filename(image_file.filename)
                image_filename = f"{species_type}_{timestamp}_{sanitized_filename}"
                # Use forward slashes for paths
                image_path = f"images/{image_filename}"
                full_image_path = os.path.join(self.images_dir, image_filename)
                
                print(f"Saving image to: {full_image_path}")
                
                # Save the image
                with open(full_image_path, "wb") as buffer:
                    shutil.copyfileobj(image_file.file, buffer)

            # Save to CSV
            csv_file = os.path.join(self.sightings_dir, f"{species_type}.csv")
            print(f"Saving to CSV: {csv_file}")
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    species_name,
                    common_name,
                    latitude,
                    longitude,
                    location_description,
                    notes,
                    image_path
                ])

            # Update knowledge base TXT file
            self._update_knowledge_base(species_type, species_name, common_name,
                                     latitude, longitude, notes, location_description)
            
            # Reinitialize RAG system to include the new sighting
            print("Updating RAG system with new sighting...")
            self.rag_system.initialize_knowledge_base()
            print("RAG system updated successfully")

            return True

        except Exception as e:
            print(f"Error saving sighting: {str(e)}")
            return False

    def _update_knowledge_base(self, species_type: str, species_name: str,
                             common_name: str, latitude: float, longitude: float,
                             notes: str, location_description: str):
        """Append new sighting information to the knowledge base TXT file."""
        if species_type in ["birds", "mammals", "plants", "other"]:
            txt_file = os.path.join(self.knowledge_dir, f"margalla_{species_type}.txt")
            
            if os.path.exists(txt_file):
                with open(txt_file, 'a') as f:
                    f.write(f"\n\nRecent Sighting ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
                    f.write(f"\n- {species_name}")
                    if common_name:
                        f.write(f" ({common_name})")
                    f.write(f"\n  Location: {location_description if location_description else f'({latitude}, {longitude})'}")
                    if notes:
                        f.write(f"\n  Notes: {notes}")

    def get_recent_sightings(self, species_type: str, limit: int = 5) -> list:
        """Get recent sightings for a specific species type."""
        csv_file = os.path.join(self.sightings_dir, f"{species_type}.csv")
        if not os.path.exists(csv_file):
            return []

        sightings = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            sightings = list(reader)[-limit:]  # Get last 'limit' entries

        return sightings 