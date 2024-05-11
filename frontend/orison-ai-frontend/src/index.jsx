// ./index.jsx

// React
import React from 'react';
import { createRoot } from 'react-dom/client';

// Chakra
import { ChakraProvider } from '@chakra-ui/react';

// Firebase
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Internal
import App from './App';
import theme from './common/theme';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDt1iKNn_Lcr0WxlPkB9re7TIsO9Zqowek",
  authDomain: "orison-ai-visa-review.firebaseapp.com",
  projectId: "orison-ai-visa-review",
  storageBucket: "orison-ai-visa-review.appspot.com",
  messagingSenderId: "253912522017",
  appId: "1:253912522017:web:31af271fc1a46708df7260",
  measurementId: "G-B1Z2968M43"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);