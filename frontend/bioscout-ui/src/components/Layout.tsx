import React from 'react';
import {
  AppBar,
  Box,
  Container,
  Toolbar,
  Typography,
  Button,
  useTheme,
} from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import NaturePeopleIcon from '@mui/icons-material/NaturePeople';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'View Observations' },
    { path: '/submit', label: 'Submit Observation' },
    { path: '/ask', label: 'Ask Questions' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper',
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Container maxWidth="lg">
          <Toolbar sx={{ px: { xs: 0 } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 0, mr: 4 }}>
              <NaturePeopleIcon 
                sx={{ 
                  color: 'primary.main',
                  fontSize: 32,
                  mr: 1,
                }} 
              />
              <Typography
                variant="h6"
                component={RouterLink}
                to="/"
                sx={{
                  color: 'text.primary',
                  textDecoration: 'none',
                  fontWeight: 600,
                  letterSpacing: '-0.5px',
                }}
              >
                BioScout
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 1 }}>
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  component={RouterLink}
                  to={item.path}
                  sx={{
                    color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                    fontWeight: location.pathname === item.path ? 600 : 500,
                    '&:hover': {
                      color: 'primary.main',
                      backgroundColor: 'transparent',
                    },
                    px: 2,
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      <Container 
        maxWidth="lg" 
        sx={{ 
          py: 3,
          height: 'calc(100vh - 64px)',
          overflow: 'auto',
        }}
      >
        {children}
      </Container>
    </Box>
  );
};

export default Layout; 