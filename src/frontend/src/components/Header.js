import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useTheme } from '../ThemeContext';
import {
    Bars3Icon,
    XMarkIcon,
    SunIcon,
    MoonIcon,
    Cog6ToothIcon
} from '@heroicons/react/24/outline';

const Header = ({ sidebarOpen, setSidebarOpen }) => {
    const { user, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const [showSettings, setShowSettings] = useState(false);

    return (
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                    >
                        {sidebarOpen ? (
                            <XMarkIcon className="h-6 w-6" />
                        ) : (
                            <Bars3Icon className="h-6 w-6" />
                        )}
                    </button>
                    <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                        Drive Connector
                    </h1>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative">
                        <button
                            onClick={() => setShowSettings(!showSettings)}
                            className="p-2 rounded-md text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                        >
                            <Cog6ToothIcon className="h-6 w-6" />
                        </button>

                        {showSettings && (
                            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                                <button
                                    onClick={() => {
                                        toggleTheme();
                                        setShowSettings(false);
                                    }}
                                    className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                                >
                                    {isDark ? (
                                        <SunIcon className="h-4 w-4" />
                                    ) : (
                                        <MoonIcon className="h-4 w-4" />
                                    )}
                                    {isDark ? 'Light Mode' : 'Dark Mode'}
                                </button>
                            </div>
                        )}
                    </div>

                    {user && (
                        <div className="flex items-center gap-2">
                            <img
                                src={user.photoURL}
                                alt={user.displayName}
                                className="h-8 w-8 rounded-full"
                            />
                            <button
                                onClick={logout}
                                className="text-sm text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white"
                            >
                                Sign Out
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
