import streamlit as st
import requests
from datetime import date
import os
from pathlib import Path
from PIL import Image
import io
from streamlit_folium import st_folium
import folium

# Hide the default sidebar that shows "< Collapse sidebar"
st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] {
        display: none
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

def display_observation_tile(sighting):
    """Display a single observation as a tile."""
    with st.container():
        # Add custom CSS for the tile
        st.markdown("""
        <style>
        .observation-tile {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .observation-tile:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .species-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .observation-details {
            color: #666;
            font-size: 0.9em;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create tile content
        tile_html = f"""
        <div class="observation-tile">
            <div class="species-name">{sighting['species_name']}</div>
            <div class="observation-details">
                Common Name: {sighting.get('common_name', 'Unknown')}<br>
                Date: {sighting.get('date', 'Unknown')}<br>
                Location: {sighting.get('location_description', 'Unknown')}
            </div>
        </div>
        """
        st.markdown(tile_html, unsafe_allow_html=True)

        # Display image if available
        if sighting.get('image_path'):
            try:
                image_path = SIGHTINGS_DIR / sighting['image_path']
                image = load_image(image_path)
                if image:
                    st.image(image, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load image: {str(e)}")

        # Display additional details
        if sighting.get('notes'):
            with st.expander("Notes"):
                st.write(sighting['notes'])

def display_observations_grid(sightings, columns=3):
    """Display observations in a grid layout."""
    cols = st.columns(columns)
    for idx, sighting in enumerate(sightings):
        with cols[idx % columns]:
            display_observation_tile(sighting)

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

    # Show sidebar only in observations tab
    with st.sidebar:
        st.subheader("Filters")
        
        # Date range filter
        st.date_input("Date Range", [])
        
        # Species type filter
        species_types = ["All", "Birds", "Mammals", "Plants", "Amphibians", "Reptiles", "Insects"]
        selected_type = st.multiselect("Species Type", species_types, default="All")
        
        # Search by name
        search_term = st.text_input("Search by species name")
        
        # Sort options
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Species Name (A-Z)", "Species Name (Z-A)"])
        
        # View options
        view_type = st.radio("View Type", ["Grid", "List", "Map"])
        
        # Apply filters button
        apply_filters = st.button("Apply Filters")

    # Toggle between map and grid view
    if view_type == "Map":
        # Create a map centered on Islamabad
        m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LNG], 
                      zoom_start=11,
                      tiles="OpenStreetMap",
                      dragging=True,  # Allow panning
                      scrollWheelZoom=True,  # Allow zoom with scroll wheel
                      zoomControl=True,  # Show zoom controls
                      doubleClickZoom=False)  # Disable double-click zoom
        
        # Disable click events
        m.add_child(folium.ClickForMarker(popup=None))  # This actually removes click functionality
        
        # Add markers for all observations
        for species_type in ["birds", "mammals", "plants", "amphibians", "reptiles", "insects"]:
            try:
                response = requests.get(f"http://localhost:8000/recent-sightings/{species_type}")
                if response.status_code == 200:
                    sightings = response.json()
                    for sighting in sightings:
                        if sighting.get('latitude') and sighting.get('longitude'):
                            folium.Marker(
                                [float(sighting['latitude']), float(sighting['longitude'])],
                                popup=f"{sighting['species_name']} ({sighting.get('common_name', 'Unknown')})",
                                icon=folium.Icon(color='red', icon='info-sign')
                            ).add_to(m)
            except Exception as e:
                st.error(f"Error loading {species_type} sightings: {str(e)}")
        
        # Display the map with disabled click events
        st_folium(m, width=800, height=600, returned_objects=[])  # Empty returned_objects disables click handling
    else:
        # Grid or List view
        all_sightings = []
        for species_type in ["birds", "mammals", "plants", "amphibians", "reptiles", "insects"]:
            try:
                response = requests.get(f"http://localhost:8000/recent-sightings/{species_type}")
                if response.status_code == 200:
                    sightings = response.json()
                    for sighting in sightings:
                        sighting['type'] = species_type
                        all_sightings.append(sighting)
            except Exception as e:
                st.error(f"Error loading {species_type} sightings: {str(e)}")

        # Apply filters
        if selected_type != ["All"]:
            all_sightings = [s for s in all_sightings if s['type'].title() in selected_type]
        
        if search_term:
            all_sightings = [s for s in all_sightings if search_term.lower() in s['species_name'].lower()]
        
        # Apply sorting
        if sort_by == "Newest First":
            all_sightings.sort(key=lambda x: x.get('date', ''), reverse=True)
        elif sort_by == "Oldest First":
            all_sightings.sort(key=lambda x: x.get('date', ''))
        elif sort_by == "Species Name (A-Z)":
            all_sightings.sort(key=lambda x: x['species_name'])
        elif sort_by == "Species Name (Z-A)":
            all_sightings.sort(key=lambda x: x['species_name'], reverse=True)

        # Display observations based on view type
        if view_type == "Grid":
            display_observations_grid(all_sightings, columns=3)
        else:  # List view
            for sighting in all_sightings:
                display_observation_tile(sighting)

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

