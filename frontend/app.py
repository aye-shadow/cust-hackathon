import streamlit as st
import requests
from datetime import date
import os
from pathlib import Path
from PIL import Image
import io
from streamlit_folium import st_folium
import folium

st.title("🦋 BioScout: Islamabad Biodiversity Explorer")

# Set up base paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / "data"
SIGHTINGS_DIR = DATA_DIR / "sightings"
IMAGES_DIR = SIGHTINGS_DIR / "images"

# Default center coordinates for Islamabad
DEFAULT_LAT = 33.6844
DEFAULT_LNG = 73.0479

def load_image(image_path):
    """Helper function to load and validate images."""
    try:
        if isinstance(image_path, (str, Path)):
            # Load from file path
            if not os.path.exists(str(image_path)):
                st.warning(f"Image not found: {image_path}")
                return None
                
            # Check if file is empty
            if os.path.getsize(str(image_path)) == 0:
                st.warning(f"Image file is empty: {image_path}")
                return None
                
            try:
                with Image.open(str(image_path)) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    # Return a copy of the image
                    return img.copy()
            except Exception as e:
                st.warning(f"Failed to open image {image_path}: {str(e)}")
                return None
        elif hasattr(image_path, 'read'):
            # Handle BytesIO or file-like objects
            try:
                with Image.open(image_path) as img:
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    return img.copy()
            except Exception as e:
                st.warning(f"Failed to open image from file object: {str(e)}")
                return None
        else:
            st.warning(f"Invalid image source: {type(image_path)}")
            return None
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

def display_sightings(col, species_type, emoji):
    """Helper function to display sightings with proper image handling."""
    with col:
        st.markdown(f"### {emoji} {species_type.title()}")
        response = requests.get(f"http://localhost:8000/recent-sightings/{species_type}")
        if response.status_code == 200:
            sightings = response.json()
            if not sightings:
                st.info(f"No {species_type} sightings recorded yet.")
            else:
                for sighting in sightings:
                    with st.expander(f"{sighting['species_name']} ({sighting.get('common_name', 'Unknown')})"):
                        st.markdown(f"**Date:** {sighting.get('date', 'Unknown')}")
                        st.markdown(f"**Location:** {sighting.get('location_description', 'Unknown')}")
                        if sighting.get('notes'):
                            st.markdown(f"**Notes:** {sighting['notes']}")
                        if sighting.get('image_path'):
                            try:
                                # Construct absolute path
                                image_path = SIGHTINGS_DIR / sighting['image_path']
                                image = load_image(image_path)
                                if image:
                                    st.image(image, use_container_width=True)
                                else:
                                    st.warning(f"Could not load image for {sighting['species_name']}")
                            except Exception as img_e:
                                st.error(f"Could not display image: {str(img_e)}")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Submit Observation", "View Observations", "Ask Questions"])

with tab1:
    # Initialize session state for coordinates if not exists
    if 'selected_lat' not in st.session_state:
        st.session_state.selected_lat = DEFAULT_LAT
    if 'selected_lng' not in st.session_state:
        st.session_state.selected_lng = DEFAULT_LNG

    st.subheader("📍 Select Location")
    st.markdown("Click on the map to select the observation location:")
    
    # Create folium map
    m = folium.Map(location=[st.session_state.selected_lat, st.session_state.selected_lng], 
                   zoom_start=11,
                   tiles="OpenStreetMap")
    
    # Add marker for current location
    folium.Marker(
        [st.session_state.selected_lat, st.session_state.selected_lng],
        popup="Selected Location",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Render the map and capture click
    map_output = st_folium(m, width=700, height=500)
    
    # Update if map is clicked
    if map_output and map_output.get("last_clicked"):
        st.session_state.selected_lat = map_output["last_clicked"]["lat"]
        st.session_state.selected_lng = map_output["last_clicked"]["lng"]

    with st.form("upload_form"):
        image = st.file_uploader("Upload an image of a species", type=["jpg", "jpeg", "png"])
        
        # Display selected coordinates
        st.markdown(f"**Selected Location:** {st.session_state.selected_lat:.4f}, {st.session_state.selected_lng:.4f}")
        
        # Hidden inputs for coordinates
        lat = st.session_state.selected_lat
        lng = st.session_state.selected_lng
        
        date_observed = st.date_input("Date Observed", value=date.today())
        location_desc = st.text_input("Location Description (optional)", 
                                    help="Add a description of the location (e.g., 'Near Trail 5 viewpoint')")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Identify & Submit")

    if submitted and image:
        try:
            # Show loading message
            with st.spinner("Identifying species..."):
                # Identify species
                files = {"image": image}
                data = {"lat": lat, "lng": lng}
                id_response = requests.post("http://localhost:8000/identify/", files=files, data=data)
                
                if id_response.status_code != 200:
                    st.error(f"Error identifying species: {id_response.text}")
                else:
                    suggestions = id_response.json()
                    
                    if not suggestions:
                        st.warning("No species suggestions found. Try another image or different angle.")
                    else:
                        st.subheader("AI Species Suggestions:")
                        for s in suggestions:
                            st.markdown(f"- **{s['name']}** ({s['rank']}), confidence: {s['confidence']:.2f}%")

                        top = suggestions[0]

                        # Submit observation with image
                        image.seek(0)  # Reset file pointer
                        files = {"image": image}
                        obs_data = {
                            "species_name": top["name"],
                            "common_name": top.get("rank", ""),  # Use rank as common name if available
                            "date_observed": str(date_observed),
                            "latitude": str(lat),
                            "longitude": str(lng),
                            "location_description": location_desc,
                            "notes": notes
                        }
                        
                        try:
                            obs_response = requests.post(
                                "http://localhost:8000/observations/",
                                files=files,
                                data=obs_data
                            )
                            if obs_response.status_code == 200:
                                st.success("Observation saved!")
                                # Use the current rerun API
                                st.rerun()
                            else:
                                st.error(f"Error saving observation: {obs_response.text}")
                        except Exception as e:
                            st.error(f"Error saving observation: {str(e)}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

with tab2:
    st.subheader("📍 Recent Observations")
    
    # Create three columns for birds, mammals, and plants
    bird_col, mammal_col, plant_col = st.columns(3)
    
    try:
        # Display each type of sighting
        display_sightings(bird_col, "birds", "🦅")
        display_sightings(mammal_col, "mammals", "🦁")
        display_sightings(plant_col, "plants", "🌿")
                                
    except Exception as e:
        st.error(f"Error fetching observations: {str(e)}")

with tab3:
    st.subheader("🔍 Ask about Local Biodiversity")
    
    # Example questions
    st.markdown("""
    **Example questions you can ask:**
    - What birds are common in Margalla Hills?
    - Are there leopards in Islamabad?
    - What are the main conservation issues in Margalla Hills?
    - Where can I find good birdwatching spots?
    """)
    
    # Question input
    with st.form("question_form"):
        question = st.text_input("Enter your question about local biodiversity:")
        ask_button = st.form_submit_button("Ask Question")
        
    if ask_button and question:
        try:
            with st.spinner("Finding answer..."):
                response = requests.post("http://localhost:8000/ask/", data={"question": question})
                
                if response.status_code == 200:
                    result = response.json()
                    st.markdown("### Answer")
                    st.write(result["answer"])
                    
                    # Show sources
                    st.markdown("### Sources")
                    for source in result["sources"]:
                        with st.expander("View Source"):
                            st.markdown(source["text"])
        except Exception as e:
            st.error(f"Error finding answer: {str(e)}")
