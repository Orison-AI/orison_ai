"use client";  // Marks the component as a Client Component

import { initializeAnalytics } from '../common/firebaseConfig';
import { logEvent } from 'firebase/analytics';

async function handleButtonClick(event: string = "button") {
    const analytics = await initializeAnalytics();
    if (analytics) {
        logEvent(analytics, event, { label: "Button clicked" });
    }
    else {
        console.log('Firebase analytics not initialized for button click event');
    }
}

async function trackPageVisit(pageName: string = "") {
    const analytics = await initializeAnalytics();
    if (analytics) {
        logEvent(analytics, "landing", { label: pageName });
    }
    else {
        console.log('Firebase analytics not initialized for page landing event');
    }
}

export { handleButtonClick, trackPageVisit };
