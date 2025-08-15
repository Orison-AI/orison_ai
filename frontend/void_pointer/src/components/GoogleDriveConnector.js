import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import axios from 'axios';
import { db } from '../firebase';
import { doc, onSnapshot, collection, query, where, limit, getDocs, getDoc } from 'firebase/firestore';

const GoogleDriveConnector = () => {
    const { user } = useAuth();
    const [isLinked, setIsLinked] = useState(false);
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentJob, setCurrentJob] = useState(null);
    const [fileStats, setFileStats] = useState({ total: 0, loaded: 0, pending: 0 });

    // Debug: Log user changes and initialize when user is ready
    useEffect(() => {
        console.log('User changed:', user);
        if (user) {
            console.log('User is ready, initializing component...');
        }
    }, [user]);

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
            console.log('Raw files from API:', allFiles); // Debug logging
            
            // Debug: Log all MIME types found
            const allMimeTypes = [...new Set(allFiles.map(f => f.mimeType))];
            console.log('All MIME types found:', allMimeTypes);
            console.log('Total files found:', allFiles.length);
            
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
            console.log('Filtered files:', filteredFiles); // Debug logging

            setFiles(filteredFiles);

            // Calculate stats
            const loaded = filteredFiles.filter(f => f.loaded).length;
            const total = filteredFiles.length;
            const pending = total - loaded;

            console.log('File stats calculation:', { loaded, total, pending, filteredFiles }); // Debug logging

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
        if (!user) {
            console.log('No user found, skipping link status check'); // Debug logging
            return;
        }
        try {
            console.log('Checking link status for user:', user.uid); // Debug logging
            const response = await axios.get(`${authServiceUrl}/status`, {
                headers: { 'X-User-ID': user.uid }
            });
            const linked = !!response.data.linked;
            console.log('Link status response:', response.data, 'Linked:', linked); // Debug logging
            setIsLinked(linked);
        } catch (error) {
            console.error('Link status check failed:', error); // Debug logging
            setIsLinked(false);
        }
    }, [authServiceUrl, user]);

    useEffect(() => {
        if (user) {
            checkLinkStatus();
        }
    }, [user, checkLinkStatus]);

    // Listen to job status changes directly from Firestore (no backend polling!)
    useEffect(() => {
        if (!currentJob?.job_id || !user) {
            return;
        }

        console.log(`Setting up Firestore listener for job: ${currentJob.job_id}`);
        
        // Listen to job document changes in real-time
        const jobDocRef = doc(db, 'jobs', currentJob.job_id);
        const unsubscribe = onSnapshot(jobDocRef, async (docSnapshot) => {
            if (docSnapshot.exists()) {
                const jobData = { job_id: currentJob.job_id, ...docSnapshot.data() };
                console.log('Firestore job update:', jobData);
                setCurrentJob(jobData);

                // Update file stats during running job for real-time top numbers
                if (jobData.status === 'running') {
                    // Refresh stats every 10 files or for first 3 files
                    if (jobData.processed_files % 10 === 0 || jobData.processed_files <= 3) {
                        console.log(`Job running: ${jobData.processed_files}/${jobData.total_files}, refreshing stats...`);
                        await loadFiles();
                    }
                }

                // Handle job completion
                if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'cancelled') {
                    setLoading(false);
                    console.log('Job finished, refreshing file stats...');
                    await loadFiles();
                    
                    // Force component re-render to update top numbers
                    setTimeout(() => {
                        console.log('Forcing stats update...');
                        setFileStats(prev => ({ ...prev }));
                    }, 1000);
                }
            } else {
                console.log('Job document not found');
                setCurrentJob(null);
                setLoading(false);
            }
        }, (error) => {
            console.error('Firestore listener error:', error);
            setLoading(false);
        });

        return () => {
            console.log(`Cleaning up Firestore listener for job: ${currentJob.job_id}`);
            unsubscribe();
        };
    }, [currentJob?.job_id, user, loadFiles]);

    useEffect(() => {
        if (isLinked && user) {
            console.log('Drive is linked and user is ready, loading files...'); // Debug logging
            loadFiles();
            checkRunningJobs();
        }
    }, [isLinked, user]); // Add user dependency to ensure files load when both are ready

    // Debug: Log whenever fileStats changes
    useEffect(() => {
        console.log('FileStats changed:', fileStats);
    }, [fileStats]);

    // Debug: Log whenever files array changes
    useEffect(() => {
        console.log('Files array changed:', files);
    }, [files]);

    // Check for running jobs directly from Firestore when page loads
    const checkRunningJobs = useCallback(async () => {
        if (!user) return;
        
        try {
            console.log('Checking for running jobs in Firestore...');
            
            // Query Firestore for running jobs for this user (simplified to avoid index requirements)
            const jobsQuery = query(
                collection(db, 'jobs'),
                where('user_id', '==', user.uid),
                where('status', '==', 'running'),
                limit(1)
            );
            
            // Use a one-time read to find running jobs
            const snapshot = await getDocs(jobsQuery);
            
            if (!snapshot.empty) {
                const runningJobDoc = snapshot.docs[0];
                const runningJob = { job_id: runningJobDoc.id, ...runningJobDoc.data() };
                console.log('Running job found in Firestore:', runningJob);
                
                setCurrentJob(runningJob);
                setLoading(true);
                localStorage.setItem(`job_${user.uid}`, runningJob.job_id);
            } else {
                console.log('No running jobs found in Firestore');
                
                // Fallback: check localStorage for any stored job
                const storedJobId = localStorage.getItem(`job_${user.uid}`);
                if (storedJobId) {
                    console.log('Checking stored job in localStorage:', storedJobId);
                    const jobDocRef = doc(db, 'jobs', storedJobId);
                    const jobDoc = await getDoc(jobDocRef);
                    
                    if (jobDoc.exists()) {
                        const jobData = { job_id: storedJobId, ...jobDoc.data() };
                        if (jobData.status === 'running') {
                            setCurrentJob(jobData);
                            setLoading(true);
                        } else {
                            localStorage.removeItem(`job_${user.uid}`);
                        }
                    } else {
                        localStorage.removeItem(`job_${user.uid}`);
                    }
                }
            }
        } catch (error) {
            console.error('Failed to check running jobs from Firestore:', error);
        }
    }, [user]);

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

        console.log('Starting load job with stats:', fileStats); // Debug logging
        setLoading(true);

        try {
            const response = await axios.post(`${driveServiceUrl}/load`, {
                all: true
            }, {
                headers: { 'X-User-ID': user.uid }
            });

            const result = response.data;
            console.log('Load job response:', result); // Debug logging

            if (result.job_id) {
                // Job started successfully, begin polling
                const newJob = {
                    job_id: result.job_id,
                    status: 'running',
                    total_files: result.total_files,
                    processed_files: 0,
                    successful_files: 0,
                    failed_files: 0
                };
                console.log('Setting new job:', newJob); // Debug logging
                setCurrentJob(newJob);
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
                // Update local state to reflect cancellation - this will trigger the UI status card
                setCurrentJob(prev => ({
                    ...prev,
                    status: 'cancelled',
                    error: 'Job cancelled by user'
                }));
                setLoading(false);

                // Force refresh file list and stats immediately
                console.log('Job cancelled, refreshing file stats...');
                await loadFiles();
                
                // Force component re-render to update top numbers
                setTimeout(() => {
                    console.log('Forcing stats update after cancel...');
                    setFileStats(prev => ({ ...prev }));
                }, 1000);
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

        try {
            const response = await axios.post(`${driveServiceUrl}/unload`, {
                all: true
            }, {
                headers: { 'X-User-ID': user.uid }
            });

            const result = response.data;
            const message = `Unloaded ${result.removed_count} files`;
            alert(message);

            // Immediately refresh file list and stats
            await loadFiles();
            
            // Force immediate button state update
            setFileStats(prev => ({ ...prev }));

        } catch (error) {
            console.error('Failed to unload all files:', error);
            alert('Failed to unload files');
        }
    };

    const unlinkAccount = async () => {
        if (!user) return;
        try {
            await axios.delete(`${authServiceUrl}/unlink`, {
                headers: { 'X-User-ID': user.uid }
            });
            setIsLinked(false);
            setFiles([]);
            setFileStats({ total: 0, loaded: 0, pending: 0 });
            setCurrentJob(null); // Clear any existing job
        } catch (error) {
            console.error('Failed to unlink account:', error);
        }
    };

    // Helper function to determine button states
    const getButtonStates = useCallback(() => {
        const isJobRunning = currentJob && currentJob.status === 'running';
        const hasPendingFiles = fileStats.pending > 0;
        const hasLoadedFiles = fileStats.loaded > 0;
        
        console.log('Button state calculation:', {
            isJobRunning,
            hasPendingFiles,
            hasLoadedFiles,
            fileStats,
            currentJob: currentJob ? { status: currentJob.status, job_id: currentJob.job_id } : null
        });
        
        // Debug: Check if we have any files at all
        console.log('Files array length:', files.length);
        console.log('Files with loaded=true:', files.filter(f => f.loaded).length);
        console.log('Files with loaded=false:', files.filter(f => !f.loaded).length);
        
        return {
            loadButton: {
                disabled: isJobRunning || !hasPendingFiles,
                text: isJobRunning ? 'Loading...' : 'Load Files',
                className: isJobRunning || !hasPendingFiles
                    ? 'bg-gray-400 cursor-not-allowed opacity-50'
                    : 'bg-green-600 hover:bg-green-700'
            },
            unloadButton: {
                disabled: !hasLoadedFiles,
                text: 'Unload Files',
                className: !hasLoadedFiles
                    ? 'bg-gray-400 cursor-not-allowed opacity-50'
                    : 'bg-red-600 hover:bg-red-700'
            }
        };
    }, [currentJob, fileStats, files.length]);

    const buttonStates = getButtonStates();

    // Debug: Log button states whenever they change
    useEffect(() => {
        console.log('Button states updated:', buttonStates);
    }, [buttonStates]);

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
                            
                            {/* Show failed files details if any (only show real errors, not expected Google Docs export issues) */}
                            {currentJob.failed_files > 0 && currentJob.results && (
                                (() => {
                                    const uiErrors = currentJob.results.filter(r => !r.downloaded && r.show_in_ui !== false);
                                    return uiErrors.length > 0 && (
                                        <div className="mt-3 p-2 bg-red-100 dark:bg-red-800 rounded text-xs">
                                            <div className="font-medium text-red-700 dark:text-red-300 mb-1">
                                                Failed Files:
                                            </div>
                                            {uiErrors
                                                .slice(0, 3) // Show first 3 failures
                                                .map((result, idx) => (
                                                    <div key={idx} className="text-red-600 dark:text-red-400">
                                                        • {result.file_name || result.file_id}: {result.reason}
                                                    </div>
                                                ))}
                                            {uiErrors.length > 3 && (
                                                <div className="text-red-600 dark:text-red-400">
                                                    ... and {uiErrors.length - 3} more failures
                                                </div>
                                            )}
                                        </div>
                                    );
                                })()
                            )}
                            
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
                    )}

                    {/* Completed Job Status */}
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
                    )}

                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-3">
                        <button
                            onClick={loadAllPDFs}
                            className={`px-4 py-2 text-white rounded-md transition-colors ${buttonStates.loadButton.className}`}
                            disabled={buttonStates.loadButton.disabled}
                        >
                            {buttonStates.loadButton.text}
                        </button>
                        <button
                            onClick={unloadAllFiles}
                            className={`px-4 py-2 text-white rounded-md transition-colors ${buttonStates.unloadButton.className}`}
                            disabled={buttonStates.unloadButton.disabled}
                        >
                            {buttonStates.unloadButton.text}
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
