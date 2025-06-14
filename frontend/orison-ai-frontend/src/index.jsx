// ./index.jsx

// React
import React from 'react';
import { createRoot } from 'react-dom/client';

// Chakra
import { ChakraProvider } from '@chakra-ui/react';

// Internal
import App from './App';
import theme from './common/theme';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);