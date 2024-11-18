// ./context/ApplicantContext.jsx

import React, { createContext, useContext, useState } from "react";

// Create the context
const ApplicantContext = createContext();

// Context Provider
export const ApplicantProvider = ({ children }) => {
    const [selectedApplicant, setSelectedApplicant] = useState(null);

    return (
        <ApplicantContext.Provider value={{ selectedApplicant, setSelectedApplicant }}>
            {children}
        </ApplicantContext.Provider>
    );
};

// Hook to use the context
export const useApplicantContext = () => useContext(ApplicantContext);
