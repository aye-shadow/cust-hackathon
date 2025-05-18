import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { LatLng, LeafletMouseEvent } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../utils/leaflet-config';
import { Species } from '../types';
import axios from 'axios';

// Default center coordinates for Islamabad
const DEFAULT_LAT = 33.6844;
const DEFAULT_LNG = 73.0479;

const MapComponent: React.FC<{
  position: [number, number];
  onPositionChange: (lat: number, lng: number) => void;
}> = ({ position, onPositionChange }) => {
  useMapEvents({
    click(e: LeafletMouseEvent) {
      onPositionChange(e.latlng.lat, e.latlng.lng);
    },
  });

  return <Marker position={position} />;
};

const SubmitObservation: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [position, setPosition] = useState<[number, number]>([DEFAULT_LAT, DEFAULT_LNG]);
  const [image, setImage] = useState<File | null>(null);
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [locationDesc, setLocationDesc] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [suggestions, setSuggestions] = useState<Species[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const formData = new FormData();
      formData.append('image', image);
      formData.append('lat', position[0].toString());
      formData.append('lng', position[1].toString());

      // Identify species
      const identifyResponse = await axios.post('http://localhost:8000/identify/', formData);
      const suggestions = identifyResponse.data;
      setSuggestions(suggestions);

      if (suggestions.length > 0) {
        const topSuggestion = suggestions[0];
        
        // Submit observation
        const obsFormData = new FormData();
        obsFormData.append('image', image);
        obsFormData.append('species_name', topSuggestion.scientific_name);
        obsFormData.append('common_name', topSuggestion.common_name);
        obsFormData.append('date_observed', date);
        obsFormData.append('latitude', position[0].toString());
        obsFormData.append('longitude', position[1].toString());
        obsFormData.append('location_description', locationDesc);
        obsFormData.append('notes', notes);

        await axios.post('http://localhost:8000/observations/', obsFormData);
        setSuccess(true);
        
        // Reset form
        setImage(null);
        setLocationDesc('');
        setNotes('');
        setSuggestions([]);
      }
    } catch (err) {
      setError('Error submitting observation. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', overflow: 'hidden' }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 2 }}>
        Submit New Observation
      </Typography>

      <Grid container spacing={2} sx={{ height: 'calc(100% - 48px)' }}>
        {/* Map Section */}
        <Grid item xs={12} md={6} sx={{ height: isMobile ? '350px' : '100%' }}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ 
              height: '100%', 
              p: '8px !important',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <MapContainer
                center={position}
                zoom={11}
                style={{ height: 'calc(100% - 40px)', width: '100%', borderRadius: 8 }}
                scrollWheelZoom={false}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                <MapComponent
                  position={position}
                  onPositionChange={(lat, lng) => setPosition([lat, lng])}
                />
              </MapContainer>
              <Box sx={{ 
                mt: 1,
                p: 1,
                borderRadius: 1,
                backgroundColor: 'rgba(46, 125, 50, 0.05)',
                border: '1px solid rgba(46, 125, 50, 0.1)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 2,
                minHeight: '32px'
              }}>
                <Typography variant="body1" sx={{ 
                  fontFamily: 'monospace',
                  fontWeight: 600,
                  color: 'primary.main'
                }}>
                  Lat: {position[0].toFixed(6)}
                </Typography>
                <Typography variant="body1" sx={{ 
                  fontFamily: 'monospace',
                  fontWeight: 600,
                  color: 'primary.main'
                }}>
                  Lng: {position[1].toFixed(6)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Form Section */}
        <Grid item xs={12} md={6} sx={{ height: '100%', overflow: 'auto' }}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <input
                  accept="image/*"
                  type="file"
                  id="image-upload"
                  onChange={(e) => setImage(e.target.files?.[0] || null)}
                  style={{ display: 'none' }}
                />
                <label htmlFor="image-upload">
                  <Button
                    variant="contained"
                    component="span"
                    fullWidth
                    sx={{
                      height: 100,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: theme.palette.background.default,
                      border: `2px dashed ${theme.palette.primary.main}`,
                      '&:hover': {
                        backgroundColor: theme.palette.background.default,
                        opacity: 0.8,
                      },
                    }}
                  >
                    <Typography variant="body1" color="primary" gutterBottom>
                      Upload Image
                    </Typography>
                    {image && (
                      <Typography variant="body2" color="textSecondary">
                        Selected: {image.name}
                      </Typography>
                    )}
                  </Button>
                </label>

                <TextField
                  type="date"
                  label="Date Observed"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />

                <TextField
                  label="Location Description"
                  placeholder="Add a description of the location"
                  value={locationDesc}
                  onChange={(e) => setLocationDesc(e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                />

                <TextField
                  label="Notes"
                  placeholder="Add any additional notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  fullWidth
                  multiline
                  rows={3}
                />

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}

                {success && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Observation submitted successfully!
                  </Alert>
                )}

                {suggestions.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Species Suggestions:
                    </Typography>
                    {suggestions.map((s, i) => (
                      <Typography key={i} variant="body1">
                        {s.scientific_name} ({s.common_name}) - {s.confidence.toFixed(2)}% confidence
                      </Typography>
                    ))}
                  </Box>
                )}

                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Submit Observation'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SubmitObservation; 