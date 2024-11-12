// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported, Analytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyD-DL2nGP24pCQE9ySboRrRp638MvSKV0M",
    authDomain: "orison-ai-landing.firebaseapp.com",
    projectId: "orison-ai-visa-apply",
    storageBucket: "orison-ai-visa-apply.appspot.com",
    messagingSenderId: "685108028813",
    appId: "1:685108028813:web:f95b43e0d1ef40745089c4",
    measurementId: "G-KY0D6V9DW7"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
let analytics: Analytics | null = null;

// Check if the analytics module is supported and if `window` is defined
if (typeof window !== 'undefined') {
    isSupported().then((supported) => {
        if (supported) {
            analytics = getAnalytics(app);
        } else {
            console.warn('Firebase Analytics is not supported in this environment.');
        }
    }).catch((error) => {
        console.error('Error checking Firebase Analytics support:', error);
    });
}

export { app, analytics };