import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ChakraProvider, createSystem, defaultConfig } from '@chakra-ui/react';
import App from './App';

const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {},
    },
  },
  globalCss: {
    'html, body': {
      bg: 'gray.900',
      color: 'gray.100',
    },
    // Dark theme for tables
    'table': {
      bg: 'gray.800',
      color: 'gray.100',
    },
    'th': {
      bg: 'gray.700',
      color: 'gray.100',
      borderColor: 'gray.600',
    },
    'td': {
      bg: 'gray.800',
      color: 'gray.100',
      borderColor: 'gray.700',
    },
    'tr': {
      bg: 'gray.800',
      borderColor: 'gray.700',
    },
    'thead': {
      bg: 'gray.700',
    },
    'tbody': {
      bg: 'gray.800',
    },
    // Fix inputs
    'input': {
      bg: 'gray.700',
      color: 'gray.100',
      borderColor: 'gray.600',
    },
  },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ChakraProvider value={system}>
      <App />
    </ChakraProvider>
  </StrictMode>,
);
