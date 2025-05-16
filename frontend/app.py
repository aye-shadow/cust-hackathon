import streamlit as st
import requests
from datetime import date

st.title("🦋 BioScout: Islamabad Biodiversity Explorer")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Submit Observation", "View Observations", "Ask Questions"])

with tab1:
    with st.form("upload_form"):
        image = st.file_uploader("Upload an image of a species", type=["jpg", "jpeg", "png"])
        lat = st.number_input("Latitude", value=33.6844)
        lng = st.number_input("Longitude", value=73.0479)
        date_observed = st.date_input("Date Observed", value=date.today())
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

                        # Submit observation
                        obs_data = {
                            "species_name": top["name"],
                            "common_name": top.get("name", ""),
                            "date_observed": str(date_observed),
                            "latitude": lat,
                            "longitude": lng,
                            "notes": notes,
                        }
                        
                        try:
                            obs_response = requests.post("http://localhost:8000/observations/", data=obs_data)
                            if obs_response.status_code == 200:
                                st.success("Observation saved!")
                            else:
                                st.error(f"Error saving observation: {obs_response.text}")
                        except Exception as e:
                            st.error(f"Error saving observation: {str(e)}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

with tab2:
    st.subheader("📍 Recent Observations")
    try:
        obs_response = requests.get("http://localhost:8000/observations/")
        if obs_response.status_code == 200:
            obs_data = obs_response.json()
            if not obs_data:
                st.info("No observations recorded yet.")
            else:
                for obs in obs_data:
                    with st.expander(f"{obs['species_name']} - {obs['date_observed']}"):
                        st.markdown(f"**Location:** ({obs['latitude']}, {obs['longitude']})")
                        if obs['notes']:
                            st.markdown(f"**Notes:** {obs['notes']}")
        else:
            st.error(f"Error fetching observations: {obs_response.text}")
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
