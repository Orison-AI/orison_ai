// app/login/page.jsx
"use client";  // Marks the component as a Client Component

import { useEffect } from 'react';
import { handleButtonClick } from "@/utils/trackers";

export default function LogIn() {
    useEffect(() => {
        handleButtonClick("App login button clicked");
        // Directly redirects to the external site
        window.location.href = 'https://www.app.orison.ai';
    }, []);

    return (
        <div>
            <p>Redirecting to the login page...</p>
        </div>
    );
}
