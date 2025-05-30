import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Chip,
  SelectChangeEvent,
} from '@mui/material';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { LatLngTuple } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../utils/leaflet-config';
import { Sighting } from '../types';
import axios from 'axios';

const DEFAULT_LAT = 33.6844;
const DEFAULT_LNG = 73.0479;
const DEFAULT_CENTER: LatLngTuple = [DEFAULT_LAT, DEFAULT_LNG];

const ViewObservations: React.FC = () => {
  const [sightings, setSightings] = useState<Sighting[]>([]);
  const [viewType, setViewType] = useState<'grid' | 'map'>('grid');
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['all']);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  useEffect(() => {
    const fetchSightings = async () => {
      try {
        // Fetch only from observations endpoint
        const response = await axios.get('http://localhost:8000/observations/');
        const allSightings = response.data.map((obs: any) => ({
          ...obs,
          timestamp: obs.date || new Date().toISOString(),
          image_path: obs.image_url
        }));
        
        setSightings(allSightings);
      } catch (error) {
        console.error('Error fetching sightings:', error);
      }
    };

    fetchSightings();
  }, []);

  const filteredSightings = sightings
    .filter(s => {
      if (selectedTypes.includes('all')) return true;
      return s.type && selectedTypes.includes(s.type);
    })
    .filter(s => 
      (s.species_name && s.species_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (s.common_name && s.common_name.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.timestamp || '').getTime() - new Date(a.timestamp || '').getTime();
        case 'oldest':
          return new Date(a.timestamp || '').getTime() - new Date(b.timestamp || '').getTime();
        case 'nameAZ':
          return a.species_name.localeCompare(b.species_name);
        case 'nameZA':
          return b.species_name.localeCompare(a.species_name);
        default:
          return 0;
      }
    });

  const handleTypeChange = (event: SelectChangeEvent<string[]>) => {
    setSelectedTypes(event.target.value as string[]);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Recent Observations
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>View Type</InputLabel>
                <Select
                  value={viewType}
                  label="View Type"
                  onChange={(e) => setViewType(e.target.value as 'grid' | 'map')}
                >
                  <MenuItem value="grid">Grid</MenuItem>
                  <MenuItem value="map">Map</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Filter by Type</InputLabel>
                <Select
                  multiple
                  value={selectedTypes}
                  label="Filter by Type"
                  onChange={handleTypeChange}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="birds">Birds</MenuItem>
                  <MenuItem value="mammals">Mammals</MenuItem>
                  <MenuItem value="plants">Plants</MenuItem>
                  <MenuItem value="amphibians">Amphibians</MenuItem>
                  <MenuItem value="reptiles">Reptiles</MenuItem>
                  <MenuItem value="insects">Insects</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={sortBy}
                  label="Sort By"
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <MenuItem value="newest">Newest First</MenuItem>
                  <MenuItem value="oldest">Oldest First</MenuItem>
                  <MenuItem value="nameAZ">Name (A-Z)</MenuItem>
                  <MenuItem value="nameZA">Name (Z-A)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Search by species name"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {viewType === 'map' ? (
        <Card sx={{ height: 'calc(100vh - 300px)', mt: 2 }}>
          <CardContent sx={{ height: '100%', p: '12px !important' }}>
            <MapContainer
              center={DEFAULT_CENTER}
              zoom={11}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              {filteredSightings.map((sighting, index) => (
                <Marker
                  key={index}
                  position={[Number(sighting.latitude), Number(sighting.longitude)] as LatLngTuple}
                >
                  <Popup>
                    <Typography variant="subtitle1">{sighting.species_name}</Typography>
                    {sighting.common_name && (
                      <Typography variant="body2">{sighting.common_name}</Typography>
                    )}
                    <Typography variant="body2">
                      Date: {new Date(sighting.timestamp || '').toLocaleDateString()}
                    </Typography>
                    {sighting.location_description && (
                      <Typography variant="body2">
                        Location: {sighting.location_description}
                      </Typography>
                    )}
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3} sx={{ mt: 1 }}>
          {filteredSightings.map((sighting, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {sighting.species_name}
                  </Typography>
                  {sighting.common_name && (
                    <Typography variant="subtitle1" gutterBottom>
                      {sighting.common_name}
                    </Typography>
                  )}
                  <Typography variant="body2" gutterBottom>
                    Date: {new Date(sighting.timestamp || '').toLocaleDateString()}
                  </Typography>
                  {sighting.location_description && (
                    <Typography variant="body2" gutterBottom>
                      Location: {sighting.location_description}
                    </Typography>
                  )}
                  {sighting.notes && (
                    <Typography variant="body2" gutterBottom>
                      Notes: {sighting.notes}
                    </Typography>
                  )}
                  {(sighting.image_url || sighting.image_path) && (
                    <Box
                      component="img"
                      src={sighting.image_url || sighting.image_path}
                      alt={sighting.species_name}
                      sx={{
                        width: '100%',
                        height: 200,
                        objectFit: 'cover',
                        borderRadius: 1,
                        mt: 2
                      }}
                      onError={(e) => {
                        console.error('Image failed to load:', sighting.image_url || sighting.image_path);
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default ViewObservations; 