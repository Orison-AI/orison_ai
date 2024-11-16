// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported, Analytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyD-DL2nGP24pCQE9ySboRrRp638MvSKV0M",
    authDomain: "orison-ai-visa-apply.firebaseapp.com",
    projectId: "orison-ai-visa-apply",
    storageBucket: "orison-ai-visa-apply.appspot.com",
    messagingSenderId: "685108028813",
    appId: "1:685108028813:web:f95b43e0d1ef40745089c4",
    measurementId: "G-KY0D6V9DW7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
let analytics: Analytics | null = null;

/**
 * Initializes Firebase Analytics and waits until it's ready.
 * @returns {Promise<Analytics | null>} The Analytics instance or null if unsupported.
 */
async function initializeAnalytics(): Promise<Analytics | null> {
    if (typeof window === 'undefined') {
        console.warn('Analytics cannot run in a non-browser environment.');
        return null;
    }

    try {
        const supported = await isSupported();
        if (supported) {
            console.log('Firebase Analytics is supported. Initializing...');
            analytics = getAnalytics(app);
            console.log('Firebase Analytics initialized successfully.');
            return analytics;
        } else {
            console.warn('Firebase Analytics is not supported in this environment.');
            return null;
        }
    } catch (error) {
        console.error('Error during Firebase Analytics initialization:', error);
        return null;
    }
}

export { app, analytics, initializeAnalytics };