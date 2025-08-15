import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import axios from 'axios';

const GoogleDriveConnector = () => {
    const { user } = useAuth();
    const [isLinked, setIsLinked] = useState(false);
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentJob, setCurrentJob] = useState(null);
    const [fileStats, setFileStats] = useState({ total: 0, loaded: 0, pending: 0 });

    const authServiceUrl = process.env.REACT_APP_AUTH_SERVICE_URL || 'http://localhost:5001';
    const driveServiceUrl = process.env.REACT_APP_DRIVE_SERVICE_URL || 'http://localhost:5002';

    const loadFiles = useCallback(async () => {
        if (!user) return;
        setLoading(true);
        try {
            const response = await axios.get(`${driveServiceUrl}/files`, {
                headers: { 'X-User-ID': user.uid }
            });
            const allFiles = response.data.files || [];

            // Apply same MIME type filter as Google Picker
            const allowedMimeTypes = new Set([
                'application/pdf',                    // PDF files
                'application/msword',                 // Word .doc
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // Word .docx
                'text/plain',                         // Text files
                'application/vnd.google-apps.document' // Google Docs
            ]);

            const filteredFiles = allFiles.filter(file =>
                allowedMimeTypes.has(file.mimeType)
            );

            setFiles(filteredFiles);

            // Calculate stats
            const loaded = filteredFiles.filter(f => f.loaded).length;
            const total = filteredFiles.length;
            const pending = total - loaded;

            setFileStats({ total, loaded, pending });
        } catch (error) {
            const status = error?.response?.status;
            const code = error?.response?.data?.error;
            if (status === 401 && code === 'relink_required') {
                setIsLinked(false);
            }
            console.error('Failed to load files:', error?.response?.data || error.message);
        } finally {
            setLoading(false);
        }
    }, [driveServiceUrl, user]);

    const checkLinkStatus = useCallback(async () => {
        if (!user) return;
        try {
            const response = await axios.get(`${authServiceUrl}/status`, {
                headers: { 'X-User-ID': user.uid }
            });
            const linked = !!response.data.linked;
            setIsLinked(linked);
        } catch (error) {
            setIsLinked(false);
        }
    }, [authServiceUrl, user]);

    useEffect(() => {
        checkLinkStatus();
    }, [checkLinkStatus]);

    // Poll job status when there's an active job
    useEffect(() => {
        if (!currentJob || currentJob.status === 'completed' || currentJob.status === 'failed') {
            return;
        }

        const pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`${driveServiceUrl}/job/${currentJob.job_id}`, {
                    headers: { 'X-User-ID': user.uid }
                });
                const jobData = response.data;

                setCurrentJob(jobData);

                if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'cancelled') {
                    clearInterval(pollInterval);
                    setLoading(false);

                    // Show completion message
                    let message;
                    if (jobData.status === 'completed') {
                        message = `Job completed: ${jobData.successful_files} loaded, ${jobData.failed_files} failed`;
                    } else if (jobData.status === 'cancelled') {
                        message = `Job cancelled: ${jobData.successful_files} files loaded before cancellation`;
                    } else {
                        message = `Job failed: ${jobData.error}`;
                    }
                    alert(message);

                    // Refresh file list
                    await loadFiles();
                }
            } catch (error) {
                console.error('Failed to poll job status:', error);
                clearInterval(pollInterval);
                setLoading(false);
            }
        }, 2000); // Poll every 2 seconds

        return () => clearInterval(pollInterval);
    }, [currentJob, driveServiceUrl, user.uid, loadFiles]);

    useEffect(() => {
        if (isLinked) {
            loadFiles();
            checkRunningJobs();
        }
    }, [isLinked, loadFiles]);

    // Check for running jobs when page loads
    const checkRunningJobs = async () => {
        try {
            const response = await axios.get(`${driveServiceUrl}/jobs`, {
                headers: { 'X-User-ID': user.uid }
            });
            const jobs = response.data.jobs || [];
            const runningJob = jobs.find(job => job.status === 'running');

            if (runningJob) {
                setCurrentJob(runningJob);
                setLoading(true);
            }
        } catch (error) {
            console.error('Failed to check running jobs:', error);
        }
    };

    // OAuth link flow (popup)
    const linkAccount = async () => {
        if (!user) return;
        try {
            // Get auth URL from backend
            const { data } = await axios.get(`${authServiceUrl}/`, {
                headers: { 'X-User-ID': user.uid }
            });
            const authUrl = data.auth_url;
            if (!authUrl) throw new Error('Missing auth URL');

            // Open centered popup
            const width = 520, height = 600;
            const left = window.screenX + (window.outerWidth - width) / 2;
            const top = window.screenY + (window.outerHeight - height) / 2;
            const popup = window.open(
                authUrl,
                'google-oauth',
                `width=${width},height=${height},left=${left},top=${top}`
            );

            // Listen for postMessage from callback
            const onMessage = async (event) => {
                if (event.origin !== window.location.origin) return;
                const { type, code } = event.data || {};
                if (type === 'OAUTH_SUCCESS' && code) {
                    window.removeEventListener('message', onMessage);
                    try {
                        await axios.post(`${authServiceUrl}/`, { code, user_id: user.uid });
                        setIsLinked(true);
                        await loadFiles();
                    } catch (e) {
                        console.error('Code exchange failed', e?.response?.data || e.message);
                    } finally {
                        try { popup && popup.close(); } catch { }
                    }
                }
            };
            window.addEventListener('message', onMessage);

            // Fallback via localStorage polling
            const start = Date.now();
            const poll = setInterval(async () => {
                if (Date.now() - start > 120000) { clearInterval(poll); return; }
                try {
                    const raw = localStorage.getItem('oauth_result');
                    if (!raw) return;
                    const parsed = JSON.parse(raw);
                    if (parsed?.type === 'OAUTH_SUCCESS' && parsed?.code) {
                        clearInterval(poll);
                        localStorage.removeItem('oauth_result');
                        try {
                            await axios.post(`${authServiceUrl}/`, { code: parsed.code, user_id: user.uid });
                            setIsLinked(true);
                            await loadFiles();
                        } catch (e) {
                            console.error('Code exchange failed', e?.response?.data || e.message);
                        } finally {
                            try { popup && popup.close(); } catch { }
                        }
                    }
                } catch { }
            }, 500);
        } catch (e) {
            console.error('Failed to initiate linking:', e?.response?.data || e.message);
        }
    };

    // Load all PDF files
    const loadAllPDFs = async () => {
        if (fileStats.total === 0) {
            alert('No PDF files found in your Google Drive');
            return;
        }

        if (currentJob && currentJob.status === 'running') {
            alert('A job is already running. Please wait for it to complete.');
            return;
        }

        setLoading(true);

        try {
            const response = await axios.post(`${driveServiceUrl}/load`, {
                all: true
            }, {
                headers: { 'X-User-ID': user.uid }
            });

            const result = response.data;

            if (result.job_id) {
                // Job started successfully, begin polling
                setCurrentJob({
                    job_id: result.job_id,
                    status: 'running',
                    total_files: result.total_files,
                    processed_files: 0,
                    successful_files: 0,
                    failed_files: 0
                });
                // Don't set loading to false - polling will handle it
            } else {
                // No files to process
                setLoading(false);
                alert(result.message);
            }

        } catch (error) {
            setLoading(false);
            console.error('Failed to start loading job:', error);
            const errorMsg = error?.response?.data?.message || 'Failed to start loading';
            alert(`Error: ${errorMsg}`);
        }
    };

    // Cancel current job
    const cancelCurrentJob = async () => {
        if (!currentJob || currentJob.status !== 'running') {
            return;
        }

        try {
            const response = await axios.post(`${driveServiceUrl}/job/${currentJob.job_id}/cancel`, {}, {
                headers: { 'X-User-ID': user.uid }
            });

            if (response.data.success) {
                // Update local state to reflect cancellation
                setCurrentJob(prev => ({
                    ...prev,
                    status: 'cancelled',
                    error: 'Job cancelled by user'
                }));
                setLoading(false);

                // Refresh file list to get updated counts
                await loadFiles();
            }
        } catch (error) {
            console.error('Failed to cancel job:', error);
            alert('Failed to cancel job. It may have already completed.');
        }
    };

    // Unload all files
    const unloadAllFiles = async () => {
        if (fileStats.loaded === 0) {
            alert('No files are currently loaded');
            return;
        }

        // DON'T set loading state for unload - it breaks button highlighting
        try {
            const response = await axios.post(`${driveServiceUrl}/unload`, {
                all: true
            }, {
                headers: { 'X-User-ID': user.uid }
            });

            const result = response.data;
            const message = `Unloaded ${result.removed_count} files`;
            alert(message);

            await loadFiles(); // Refresh file list and stats

        } catch (error) {
            console.error('Failed to unload all files:', error);
            alert('Failed to unload files');
        }
        // No finally block setting loading to false
    }; const unlinkAccount = async () => {
        if (!user) return;
        try {
            await axios.delete(`${authServiceUrl}/unlink`, {
                headers: { 'X-User-ID': user.uid }
            });
            setIsLinked(false);
            setFiles([]);
            setFileStats({ total: 0, loaded: 0, pending: 0 });
        } catch (error) {
            console.error('Failed to unlink account:', error);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <svg className="w-8 h-8" viewBox="0 0 24 24" aria-hidden="true">
                        <path fill="#4285F4" d="M6 2c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6H6z" />
                        <path fill="#34A853" d="M14 2l6 6h-6V2z" />
                        <path fill="#FBBC04" d="M6 2v6h8V2H6z" />
                        <path fill="#EA4335" d="M6 8v12h12V8H6z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Google Drive</h3>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${isLinked
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                    }`}>
                    {isLinked ? 'Connected' : 'Not Connected'}
                </span>
            </div>

            {!isLinked ? (
                <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                        Connect your Google Drive to browse and import files securely.
                    </p>
                    <button
                        onClick={linkAccount}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                        disabled={loading}
                    >
                        {loading ? 'Connecting...' : 'Connect Google Drive'}
                    </button>
                </div>
            ) : (
                <div className="space-y-4">
                    {/* File Detection Status */}
                    <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                {fileStats.total}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-300">
                                Total Files
                            </div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                                {fileStats.loaded}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-300">
                                Loaded
                            </div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                                {fileStats.pending}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-300">
                                Pending
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar - Shows persistent job progress */}
                    {currentJob && currentJob.status === 'running' && (
                        <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                                    Loading files... (Job ID: {currentJob.job_id.slice(0, 8)})
                                </span>
                                <span className="text-sm text-blue-600 dark:text-blue-400">
                                    {currentJob.processed_files} / {currentJob.total_files}
                                </span>
                            </div>
                            <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2 mb-2">
                                <div
                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{
                                        width: `${currentJob.total_files > 0 ? (currentJob.processed_files / currentJob.total_files) * 100 : 0}%`
                                    }}
                                ></div>
                            </div>
                            <div className="flex justify-between text-xs text-blue-600 dark:text-blue-400 mb-3">
                                <span>✅ {currentJob.successful_files} loaded</span>
                                <span>❌ {currentJob.failed_files} failed</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <p className="text-xs text-blue-500 dark:text-blue-300">
                                    💡 You can close this tab and come back - progress is saved!
                                </p>
                                <button
                                    onClick={cancelCurrentJob}
                                    className="px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                                >
                                    Cancel Job
                                </button>
                            </div>
                        </div>
                    )}                    {/* Completed Job Status */}
                    {currentJob && currentJob.status === 'completed' && (
                        <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-green-700 dark:text-green-300">
                                    ✅ Loading completed!
                                </span>
                                <button
                                    onClick={() => setCurrentJob(null)}
                                    className="text-xs text-green-600 dark:text-green-400 hover:underline"
                                >
                                    Dismiss
                                </button>
                            </div>
                            <div className="flex justify-between text-xs text-green-600 dark:text-green-400">
                                <span>✅ {currentJob.successful_files} files loaded successfully</span>
                                <span>❌ {currentJob.failed_files} failed</span>
                            </div>
                        </div>
                    )}

                    {/* Failed Job Status */}
                    {currentJob && currentJob.status === 'failed' && (
                        <div className="p-4 bg-red-50 dark:bg-red-900 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-red-700 dark:text-red-300">
                                    ❌ Loading failed
                                </span>
                                <button
                                    onClick={() => setCurrentJob(null)}
                                    className="text-xs text-red-600 dark:text-red-400 hover:underline"
                                >
                                    Dismiss
                                </button>
                            </div>
                            <p className="text-xs text-red-600 dark:text-red-400">
                                {currentJob.error || 'An error occurred during file loading'}
                            </p>
                        </div>
                    )}

                    {/* Cancelled Job Status */}
                    {currentJob && currentJob.status === 'cancelled' && (
                        <div className="p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                                    ⏹️ Loading cancelled
                                </span>
                                <button
                                    onClick={() => setCurrentJob(null)}
                                    className="text-xs text-yellow-600 dark:text-yellow-400 hover:underline"
                                >
                                    Dismiss
                                </button>
                            </div>
                            <div className="flex justify-between text-xs text-yellow-600 dark:text-yellow-400">
                                <span>✅ {currentJob.successful_files} files loaded before cancellation</span>
                                <span>❌ {currentJob.failed_files} failed</span>
                            </div>
                            <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-2">
                                Job was stopped at {currentJob.processed_files} of {currentJob.total_files} files
                            </p>
                        </div>
                    )}                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-3">
                        <button
                            onClick={loadAllPDFs}
                            className={`px-4 py-2 text-white rounded-md transition-colors ${(currentJob && currentJob.status === 'running') || fileStats.pending === 0
                                    ? 'bg-gray-400 cursor-not-allowed opacity-50'
                                    : 'bg-green-600 hover:bg-green-700'
                                }`}
                            disabled={(currentJob && currentJob.status === 'running') || fileStats.pending === 0}
                        >
                            {(currentJob && currentJob.status === 'running') ? 'Loading...' : `Load ${fileStats.pending} PDFs`}
                        </button>
                        <button
                            onClick={unloadAllFiles}
                            className={`px-4 py-2 text-white rounded-md transition-colors ${fileStats.loaded === 0
                                    ? 'bg-gray-400 cursor-not-allowed opacity-50'
                                    : 'bg-red-600 hover:bg-red-700'
                                }`}
                            disabled={fileStats.loaded === 0}
                        >
                            Unload ${fileStats.loaded} Files
                        </button>
                    </div>

                    <div className="flex justify-center">
                        <button
                            onClick={unlinkAccount}
                            className="px-4 py-2 bg-gray-200 text-gray-900 rounded-md hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600"
                        >
                            Disconnect
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GoogleDriveConnector;
