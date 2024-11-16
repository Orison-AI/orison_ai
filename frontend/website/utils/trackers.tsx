"use client";  // Marks the component as a Client Component

import { analytics } from '../common/firebaseConfig';
import { logEvent } from 'firebase/analytics';

function handleButtonClick(event_label: string = "") {
    if (analytics) {
        logEvent(analytics, "button_click", { label: event_label });
    }
    else {
        console.log('Firebase analytics not initialized');
    }
}

function trackPageVisit(pageName: string = "") {
    if (analytics) {
        logEvent(analytics, 'landing', { page_name: pageName });
    }
    else {
        console.log('Firebase analytics not initialized');
    }
}

export { handleButtonClick, trackPageVisit };
