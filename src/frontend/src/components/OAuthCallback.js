import React, { useEffect, useState } from 'react';

const OAuthCallback = () => {
    const [status, setStatus] = useState('processing');
    const [message, setMessage] = useState('Completing authentication...');

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        if (code) {
            setStatus('success');
            setMessage('Authentication successful! Closing window...');

            try {
                // Try to notify parent; avoid reading opener.closed due to COOP
                if (window.opener) {
                    window.opener.postMessage(
                        { type: 'OAUTH_SUCCESS', code },
                        window.location.origin
                    );
                }
            } catch (e) {
                console.error('postMessage failed:', e);
            }

            // Always write to localStorage as fallback
            try {
                localStorage.setItem('oauth_result', JSON.stringify({
                    type: 'OAUTH_SUCCESS',
                    code: code,
                    timestamp: Date.now()
                }));
            } catch (e) {
                console.error('localStorage write failed:', e);
            }

            // Attempt to close; if blocked, show manual close hint
            setTimeout(() => {
                try { window.close(); } catch { }
                setTimeout(() => { setMessage('You can close this window.'); }, 800);
            }, 1000);
        } else if (error) {
            setStatus('error');
            setMessage(`Authentication failed: ${error}`);
            try {
                if (window.opener) {
                    window.opener.postMessage(
                        { type: 'OAUTH_ERROR', error },
                        window.location.origin
                    );
                }
            } catch { }
            try {
                localStorage.setItem('oauth_result', JSON.stringify({
                    type: 'OAUTH_ERROR',
                    error: error,
                    timestamp: Date.now()
                }));
            } catch { }
            setTimeout(() => { try { window.close(); } catch { } }, 1500);
        } else {
            setStatus('error');
            setMessage('No authorization code received.');
        }
    }, []);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
            <div className="text-center max-w-md mx-auto p-6">
                {status === 'processing' && (
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                )}
                {status === 'success' && (
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                )}
                {status === 'error' && (
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </div>
                )}
                <p className="text-gray-600 dark:text-gray-400">{message}</p>
            </div>
        </div>
    );
};

export default OAuthCallback;
