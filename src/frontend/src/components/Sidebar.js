import React from 'react';
import GoogleDriveConnector from './GoogleDriveConnector';

const Sidebar = ({ isOpen }) => {
    return (
        <div className={`${isOpen ? 'translate-x-0' : '-translate-x-full'
            } fixed inset-y-0 left-0 z-50 w-80 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
            <div className="flex flex-col h-full">
                <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
                    <div className="flex-1 px-3 bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        <div className="space-y-1">
                            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                                Available Connectors
                            </h2>
                            <GoogleDriveConnector />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
