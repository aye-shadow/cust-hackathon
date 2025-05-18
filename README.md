# BioScout - Biodiversity Tracking Application

BioScout is a modern web application for tracking and monitoring local biodiversity. It allows users to submit wildlife observations, view sightings on an interactive map, and get AI-powered answers about local biodiversity.

## Features

### 1. Submit Observations
- Upload images of wildlife sightings
- Automatic species identification using AI
- Interactive map for precise location marking
- Detailed form for recording:
  - Date of observation
  - Location coordinates (with visual confirmation)
  - Location description
  - Additional notes
- Real-time feedback and validation

### 2. View Observations
- Grid and map view options
- Filter observations by species type:
  - Birds
  - Mammals
  - Plants
  - Amphibians
  - Reptiles
  - Insects
- Up to 50 recent sightings per species type
- Interactive markers on map view
- Detailed observation cards with images

### 3. Ask Questions
- AI-powered Q&A about local biodiversity
- Example questions provided
- Detailed answers with source citations
- Focus on local wildlife and conservation

## Technical Stack

### Frontend
- React with TypeScript
- Material-UI (MUI) for components
- Custom nature-inspired theme
- Leaflet for interactive maps
- Responsive design for all devices

### Backend
- FastAPI
- Image processing and storage
- CSV-based data management
- Species identification AI integration

## Theme Design

The application features a bio-inspired design with:
- Rich forest greens and honey amber colors
- Subtle gradients and animations
- Organic shapes and decorative elements
- Custom styled components:
  - Cards with gradient borders
  - Light green buttons with hover effects
  - Frosted glass navigation bar
  - Custom form inputs with shadows
  - Nature-themed icons

## Setup Instructions

1. Clone the repository:
```bash
git clone [repository-url]
cd bioscout
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend/bioscout-ui
npm install
```

4. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

5. Start the frontend development server:
```bash
cd frontend/bioscout-ui
npm start
```

The application will be available at `http://localhost:3000`

## Data Management

- Observations are stored in CSV files by species type
- Images are stored in `data/sightings/images`
- Data can be reset using the cleanup process

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
