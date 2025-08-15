import React, { useState } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import { ThemeProvider } from './ThemeContext';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import OAuthCallback from './components/OAuthCallback';

const AppContent = () => {
    const { user, loading } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="text-gray-500 dark:text-gray-400">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return <Login />;
    }

    return (
        <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
            <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

            <div className="flex-1 flex overflow-hidden">
                <Sidebar isOpen={sidebarOpen} />

                {sidebarOpen && (
                    <div
                        className="fixed inset-0 bg-black bg-opacity-25 lg:hidden z-40"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}

                <div className="flex-1 overflow-hidden">
                    <ChatInterface />
                </div>
            </div>
        </div>
    );
};

const App = () => {
    return (
        <ThemeProvider>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/oauth/callback" element={<OAuthCallback />} />
                        <Route path="/*" element={<AppContent />} />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </ThemeProvider>
    );
};

export default App;
