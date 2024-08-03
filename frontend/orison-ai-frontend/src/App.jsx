// ./App.jsx

// React
import React, { useEffect, useState } from 'react';

// Firebase
import { onAuthStateChanged } from "firebase/auth";

// Chakra
import { Box, Text, useDisclosure, VStack } from '@chakra-ui/react';

// Internal
import { auth } from './common/firebaseConfig';
import ApplicantDocuments from './components/pages/ApplicantDocuments/ApplicantDocuments';
import ApplicantSummarization from './components/pages/ApplicantSummarization/ApplicantSummarization';
import Auth from './components/auth/Auth';
import Header from './components/Header';
import ManageApplicants from './components/pages/ManageApplicants/ManageApplicants';
import Navigation from './components/Navigation';
import Settings from './components/settings/Settings';
import Views from './common/views';

const App = () => {
  const [user, setUser] = useState(null);
  const { isSettingsOpen, onSettingsOpen, onSettingsClose } = useDisclosure();
  const [currentView, setCurrentView] = useState(Views.MANAGE_APPLICANTS);
  const [applicants, setApplicants] = useState([]);
  const [selectedApplicant, setSelectedApplicant] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        // User is signed in
        setUser(currentUser);
      } else {
        // No user is signed in
        setUser(null);
      }
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  if (!user) {
    return <Auth />;
  }

  const renderCurrentView = () => {
    switch(currentView) {
      case Views.MANAGE_APPLICANTS:
        return <ManageApplicants
          applicants={applicants}
          setApplicants={setApplicants}
          selectedApplicant={selectedApplicant}
          setSelectedApplicant={setSelectedApplicant}
          setCurrentView={setCurrentView}
        />;
      case Views.APPLICANT_DOCUMENTS:
        return <ApplicantDocuments selectedApplicant={selectedApplicant} />;
      case Views.APPLICANT_SUMMARIZATION:
        return <ApplicantSummarization selectedApplicant={selectedApplicant} />;
      default:
        return <Text>Invalid View</Text>
    }
  };

  return (
    <VStack height="100vh" width="100vw">
      <Header onSettingsOpen={onSettingsOpen} />
      {currentView !== Views.MANAGE_APPLICANTS && (
        <Navigation
          applicants={applicants}
          selectedApplicant={selectedApplicant}
          setSelectedApplicant={setSelectedApplicant}
          currentView={currentView}
          setCurrentView={setCurrentView}
        />
      )}
      <Settings isOpen={isSettingsOpen} onClose={onSettingsClose} />
      <Box width="100%" flex="1" overflowY="auto">
        {renderCurrentView()}
      </Box>
    </VStack>
  );
}

export default App;
