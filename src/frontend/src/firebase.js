import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyD-DL2nGP24pCQE9ySboRrRp638MvSKV0M",
    authDomain: "orison-ai-visa-apply.firebaseapp.com",
    projectId: "orison-ai-visa-apply",
    storageBucket: "orison-ai-visa-apply.appspot.com",
    messagingSenderId: "685108028813",
    appId: "1:685108028813:web:06164ab1ea0a4f765089c4",
    measurementId: "G-0X5RE57SDJ"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);