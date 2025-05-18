import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Paper,
} from '@mui/material';
import { QuestionResponse } from '../types';
import axios from 'axios';

const EXAMPLE_QUESTIONS = [
  'What birds are common in Margalla Hills?',
  'Are there leopards in Islamabad?',
  'What are the main conservation issues in Margalla Hills?',
  'Where can I find good birdwatching spots?',
];

const AskQuestions: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QuestionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Create FormData object
      const formData = new FormData();
      formData.append('question', question.trim());

      const response = await axios.post<QuestionResponse>(
        'http://localhost:8000/ask/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setResponse(response.data);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError(`Failed to get an answer: ${err.response.data.detail || 'Please try again.'}`);
      } else {
        setError('Failed to get an answer. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Ask about Local Biodiversity
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Example Questions
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {EXAMPLE_QUESTIONS.map((q, i) => (
              <Button
                key={i}
                variant="outlined"
                size="small"
                onClick={() => setQuestion(q)}
                sx={{ mb: 1 }}
              >
                {q}
              </Button>
            ))}
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Enter your question about local biodiversity"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              multiline
              rows={2}
              sx={{ mb: 2 }}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !question.trim()}
              sx={{ minWidth: 120 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Ask Question'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {response && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Answer
            </Typography>
            <Typography paragraph>{response.answer}</Typography>

            {response.sources.length > 0 && (
              <>
                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Sources
                </Typography>
                {response.sources.map((source, index) => (
                  <Paper
                    key={index}
                    elevation={1}
                    sx={{
                      p: 2,
                      mb: 2,
                      backgroundColor: 'rgba(0, 0, 0, 0.02)',
                    }}
                  >
                    <Typography variant="body2">{source.text}</Typography>
                  </Paper>
                ))}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default AskQuestions; 