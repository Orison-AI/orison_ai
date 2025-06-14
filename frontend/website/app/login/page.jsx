// app/login/page.jsx
"use client";  // Marks the component as a Client Component

import { useEffect } from 'react';
import { handleButtonClick } from "@/utils/trackers";

export default function LogIn() {
    useEffect(() => {
        const logAndRedirect = async () => {
            try {
                await handleButtonClick("App login button clicked");
                // Directly redirects to the external site after logging
                window.location.href = 'https://www.app.orison.ai';
            } catch (error) {
                console.error("Failed to log button click:", error);
            }
        };

        logAndRedirect();
    }, []);

    return (
        <div>
            <p>Redirecting to the login page...</p>
        </div>
    );
}
