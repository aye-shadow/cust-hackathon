import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';
import Layout from './components/Layout';
import SubmitObservation from './pages/SubmitObservation';
import ViewObservations from './pages/ViewObservations';
import AskQuestions from './pages/AskQuestions';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<ViewObservations />} />
            <Route path="/submit" element={<SubmitObservation />} />
            <Route path="/ask" element={<AskQuestions />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
