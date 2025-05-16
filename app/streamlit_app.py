import streamlit as st
from datetime import date
from main import identify, add_observation, get_observations, ask_question

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
            with st.spinner("Identifying species..."):
                # Call the identify function directly
                suggestions = identify(image, lat, lng)
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
                        "date_observed": date_observed,
                        "latitude": lat,
                        "longitude": lng,
                        "notes": notes,
                    }
                    try:
                        add_observation(**obs_data)
                        st.success("Observation saved!")
                    except Exception as e:
                        st.error(f"Error saving observation: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

with tab2:
    st.subheader("📍 Recent Observations")
    try:
        obs_data = get_observations()
        if not obs_data:
            st.info("No observations recorded yet.")
        else:
            for obs in obs_data:
                with st.expander(f"{obs.species_name} - {obs.date_observed}"):
                    st.markdown(f"**Location:** ({obs.latitude}, {obs.longitude})")
                    if obs.notes:
                        st.markdown(f"**Notes:** {obs.notes}")
    except Exception as e:
        st.error(f"Error fetching observations: {str(e)}")

with tab3:
    st.subheader("🔍 Ask about Local Biodiversity")
    st.markdown("""
    **Example questions you can ask:**
    - What birds are common in Margalla Hills?
    - Are there leopards in Islamabad?
    - What are the main conservation issues in Margalla Hills?
    - Where can I find good birdwatching spots?
    """)
    with st.form("question_form"):
        question = st.text_input("Enter your question about local biodiversity:")
        ask_button = st.form_submit_button("Ask Question")
    if ask_button and question:
        try:
            with st.spinner("Finding answer..."):
                result = ask_question(question)
                st.markdown("### Answer")
                st.write(result["answer"])
                st.markdown("### Sources")
                for source in result["sources"]:
                    with st.expander("View Source"):
                        st.markdown(source["text"])
        except Exception as e:
            st.error(f"Error finding answer: {str(e)}")