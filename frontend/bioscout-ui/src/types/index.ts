export interface Sighting {
  species_name: string;
  common_name?: string;
  date: string;
  location_description?: string;
  notes?: string;
  image_path?: string;
  latitude?: string;
  longitude?: string;
  type?: string;
}

export interface Species {
  name: string;
  rank: string;
  confidence: number;
}

export interface QuestionResponse {
  answer: string;
  sources: Array<{
    text: string;
  }>;
} 