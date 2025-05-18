import { createTheme } from '@mui/material';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // Rich forest green
      light: '#4CAF50', // Leaf green
      dark: '#1B5E20', // Deep forest
    },
    secondary: {
      main: '#FF8F00', // Warm amber (like honey)
      light: '#FFB74D', // Soft honey
      dark: '#F57C00', // Deep amber
    },
    background: {
      default: '#F1F8E9', // Very light sage
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1B5E20', // Deep forest green
      secondary: '#558B2F', // Olive green
    },
    error: {
      main: '#C62828', // Berry red
    },
    warning: {
      main: '#EF6C00', // Autumn orange
    },
    success: {
      main: '#2E7D32', // Forest green
    },
    info: {
      main: '#0288D1', // River blue
    },
  },
  typography: {
    fontFamily: '"Quicksand", "Inter", "Roboto", sans-serif',
    h4: {
      fontWeight: 700,
      color: '#1B5E20',
      letterSpacing: '-0.5px',
    },
    h6: {
      fontWeight: 600,
      color: '#2E7D32',
      letterSpacing: '-0.25px',
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.5px',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 20px rgba(46, 125, 50, 0.1)',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #4CAF50, #2E7D32)',
            borderRadius: '16px 16px 0 0',
          },
          '&:hover': {
            boxShadow: '0 8px 24px rgba(46, 125, 50, 0.15)',
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 25,
          textTransform: 'none',
          fontWeight: 600,
          padding: '8px 24px',
          transition: 'all 0.3s ease',
        },
        contained: {
          background: 'rgba(46, 125, 50, 0.05)',
          boxShadow: '0 2px 12px rgba(46, 125, 50, 0.1)',
          color: '#2E7D32',
          '&:hover': {
            background: 'rgba(46, 125, 50, 0.1)',
            boxShadow: '0 4px 16px rgba(46, 125, 50, 0.15)',
            transform: 'translateY(-1px)',
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
            background: 'rgba(46, 125, 50, 0.05)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            transition: 'all 0.3s ease',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(46, 125, 50, 0.1)',
            },
            '&.Mui-focused': {
              boxShadow: '0 4px 12px rgba(46, 125, 50, 0.15)',
            },
          },
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: 'rgba(46, 125, 50, 0.2)',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: 'rgba(46, 125, 50, 0.3)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(180deg, rgba(46, 125, 50, 0.05) 0%, rgba(255, 255, 255, 0) 100%)',
          backdropFilter: 'blur(8px)',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(46, 125, 50, 0.2), transparent)',
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
        },
        standardSuccess: {
          background: 'linear-gradient(45deg, #2E7D32, #4CAF50)',
          color: '#fff',
        },
        standardError: {
          background: 'linear-gradient(45deg, #C62828, #E53935)',
          color: '#fff',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 25,
          fontWeight: 600,
          '&.MuiChip-colorPrimary': {
            background: 'linear-gradient(45deg, #2E7D32, #4CAF50)',
            boxShadow: '0 2px 8px rgba(46, 125, 50, 0.2)',
          },
          '&.MuiChip-colorSecondary': {
            background: 'linear-gradient(45deg, #FF8F00, #FFB74D)',
            boxShadow: '0 2px 8px rgba(255, 143, 0, 0.2)',
          },
        },
      },
    },
  },
}); 