import React from 'react';

const ChatInterface = () => {
    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900">
            <div className="flex-1 p-6 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        Chat Interface
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400">
                        Chat functionality will be implemented here
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
