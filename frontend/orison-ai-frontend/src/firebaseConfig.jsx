// ./firebaseConfig.jsx

// Firebase v9+ modular imports
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Firebase configuration
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
const auth = getAuth(app);
const db = getFirestore(app);

export { app, db, auth };
