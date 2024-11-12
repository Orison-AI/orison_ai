"use client";  // Marks the component as a Client Component

import { analytics } from '../common/firebaseConfig';
import { logEvent } from 'firebase/analytics';

import { useEffect } from 'react';

function handleButtonClick(event_label: string = "") {
    console.log('Sending custom event: button_click');
    if (analytics) {
        logEvent(analytics, "button_click", { label: event_label });
        console.log('Custom event logged: button_click');
    }
    else {
        console.log('Firebase analytics not initialized');
    }
}

function trackPageVisit(pageName: string) {
    console.log('Sending custom event: page_visit');
    if (analytics) {
        logEvent(analytics, 'page_visit', { page_name: pageName });
        console.log('Custom event logged: page_visit');
    }
    else {
        console.log('Firebase analytics not initialized');
    }
}

function useTrackTimeSpentOnPage(pageName: string) {
    useEffect(() => {
        const startTime = Date.now(); // Start time when the component mounts

        return () => {
            // Calculate end time when the component unmounts
            if (analytics) {
                const endTime = Date.now();
                const duration = Math.round((endTime - startTime) / 1000); // Time in seconds
                logEvent(analytics, 'time_spent_on_page', { page_name: pageName, duration });
            }
        };
    }, [pageName]); // Dependency array ensures it runs for the specified page
}

function trackSectionTime(sectionId: string) {
    let entryTime: number | null = null;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entryTime = Date.now();
            } else if (entryTime !== null) {
                const exitTime = Date.now();
                const timeSpent = Math.round((exitTime - entryTime) / 1000);
                entryTime = null;

                if (analytics) {
                    logEvent(analytics, 'time_spent_on_section', {
                        section_name: sectionId,
                        duration: timeSpent,
                    });
                }
            }
        });
    });

    const section = document.getElementById(sectionId);
    if (section) {
        observer.observe(section);
    }

    return () => {
        if (section) observer.unobserve(section);
    };
}

function trackVideoTime(videoElement: HTMLVideoElement, videoName: string) {
    let watchStartTime: number | null = null;

    videoElement.addEventListener('play', () => {
        watchStartTime = Date.now();
    });

    videoElement.addEventListener('pause', () => {
        if (watchStartTime !== null && analytics) {
            const pauseTime = Date.now();
            const timeSpent = Math.round((pauseTime - watchStartTime) / 1000);
            watchStartTime = null;
            logEvent(analytics, 'time_spent_on_video', {
                video_name: videoName,
                duration: timeSpent,
            });
        }
    });

    videoElement.addEventListener('ended', () => {
        if (watchStartTime !== null && analytics) {
            const endTime = Date.now();
            const timeSpent = Math.round((endTime - watchStartTime) / 1000);
            watchStartTime = null;
            logEvent(analytics, 'time_spent_on_video', {
                video_name: videoName,
                duration: timeSpent,
            });
        }
    });
}

export { handleButtonClick, trackPageVisit, useTrackTimeSpentOnPage, trackSectionTime, trackVideoTime };
