# 🦋 BioScout: Islamabad Biodiversity Explorer

BioScout is an AI-powered biodiversity monitoring application specifically designed for Islamabad's ecosystem, with a focus on the Margalla Hills National Park. The system helps users identify species, record observations, and learn about local biodiversity through an interactive question-answering system.

## 🌟 Features

- **Species Identification**: Upload images to identify local flora and fauna using AI
- **Observation Recording**: Log and track biodiversity sightings with location data
- **Knowledge Base**: Access information about local species through an AI-powered Q&A system
- **Interactive Interface**: User-friendly web interface with tabbed navigation

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: SQLite
- **AI/ML Components**:
  - Species Identification: iNaturalist API
  - Q&A System: Groq LLM (llama3-8b-8192)
  - Embeddings: HuggingFace (sentence-transformers)
  - Vector Store: Chroma DB

## 📋 Prerequisites

- Python 3.8+
- Groq API Key
- Internet connection for API access

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/aye-shadow/cust-hackathon.git
cd cust-hackathon
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Set up environment variables:
```bash
# Windows PowerShell
$env:GROQ_API_KEY = "your-groq-api-key"

# Linux/Mac
export GROQ_API_KEY="your-groq-api-key"
```

4. Initialize the database:
```bash
cd backend
python init_db.py
```

## 🚀 Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend application (in a new terminal):
```bash
cd frontend
streamlit run app.py
```

3. Access the application at `http://localhost:8501`

## 💡 Usage

### Species Identification
1. Navigate to the "Submit Observation" tab
2. Upload an image of the species
3. Enter location details (default is set to Islamabad coordinates)
4. Click "Identify & Submit"

### Viewing Observations
1. Go to the "View Observations" tab
2. Browse through recorded observations
3. Click on individual observations to view details

### Asking Questions
1. Select the "Ask Questions" tab
2. Type your question about local biodiversity
3. Click "Ask Question" to get AI-powered responses

## 📚 Knowledge Base

The system includes information about:
- Local bird species
- Mammal species
- Plant species
- Conservation issues
- Biodiversity hotspots

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- iNaturalist for species identification API
- Groq for LLM capabilities
- Margalla Hills National Park for biodiversity data
