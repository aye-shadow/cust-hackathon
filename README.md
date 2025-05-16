# 🦋 BioScout: Islamabad Biodiversity Explorer

BioScout is an AI-powered biodiversity monitoring application specifically designed for Islamabad's ecosystem, with a focus on the Margalla Hills National Park. The system helps users identify species, record observations, and learn about local biodiversity through an interactive question-answering system.

## 🌟 Features

- **Species Identification**: Upload images to identify local flora and fauna using AI (iNaturalist API)
- **Observation Recording**: Log and track biodiversity sightings with location data
- **Knowledge Base**: Access information about local species through an AI-powered Q&A system (Groq LLM + RAG)
- **Interactive Interface**: User-friendly web interface with tabbed navigation (Streamlit)

## 🛠️ Technology Stack

- **Frontend & App**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **AI/ML Components**:
  - Species Identification: iNaturalist API
  - Q&A System: Groq LLM (llama3-8b-8192)
  - Embeddings: HuggingFace (sentence-transformers)
  - Vector Store: Supabase

## 📋 Prerequisites

- Python 3.8+
- Supabase project (with credentials)
- Groq API Key
- iNaturalist API Token
- Internet connection for API access

## ⚙️ Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/aye-shadow/cust-hackathon.git
    cd cust-hackathon
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    - Copy `.env.example` to `.env` and fill in your Supabase, Groq, and iNaturalist credentials:
      ```
      cp .env.example .env
      ```
    - Edit `.env` and set:
      ```
      SUPABASE_DB_URL=...
      SUPABASE_URL=...
      SUPABASE_SERVICE_KEY=...
      GROQ_API_KEY=...
      INATURALIST_TOKEN=...
      ```

4. **(Optional) Initialize Supabase database:**
    - Ensure your Supabase project has a table named `observations` for storing observations and a table named `documents` for the vector store.
    - The schema for `observations` should match the fields in [`app/models.py`](app/models.py).

## 🚀 Running the Application

1. **Start the Streamlit app:**
    ```bash
    streamlit run app/streamlit_app.py
    ```

2. **Access the application:**
    - Open your browser and go to [http://localhost:8501](http://localhost:8501)

## 💡 Usage

### Species Identification
1. Navigate to the "Submit Observation" tab.
2. Upload an image of the species.
3. Enter location details (default is set to Islamabad coordinates).
4. Click "Identify & Submit" to get AI suggestions and save your observation.

### Viewing Observations
1. Go to the "View Observations" tab.
2. Browse through recorded observations.
3. Click on individual observations to view details.

### Asking Questions
1. Select the "Ask Questions" tab.
2. Type your question about local biodiversity.
3. Click "Ask Question" to get AI-powered responses with sources.

## 📚 Knowledge Base

The system includes information about:
- Local bird species ([data/margalla_birds.txt](data/margalla_birds.txt))
- Mammal species ([data/margalla_mammals.txt](data/margalla_mammals.txt))
- Plant species ([data/margalla_plants.txt](data/margalla_plants.txt))
- Conservation issues
- Biodiversity hotspots

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- iNaturalist for species identification API
- Groq for LLM capabilities
- Margalla Hills National Park for biodiversity data