export interface Species {
  scientific_name: string;
  common_name: string;
  confidence: number;
}

export interface Sighting {
  species_name: string;
  common_name?: string;
  latitude: number;
  longitude: number;
  location_description?: string;
  notes?: string;
  image_url?: string;
  image_path?: string;
  date?: string;
  timestamp?: string;
  type?: string;
}

export interface QuestionResponse {
  answer: string;
  sources: Array<{
    text: string;
    source?: string;
  }>;
} 