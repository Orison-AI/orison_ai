// ./App.jsx

// React
import React, { useEffect, useState } from 'react';

// Firebase
import { onAuthStateChanged } from "firebase/auth";

// Chakra
import { Text, useDisclosure, VStack } from '@chakra-ui/react';

// Internal

import { auth } from './firebaseConfig';
import Views from './common/views';
import Header from './components/Header';
import MainMenu from './components/MainMenu';
import Settings from './components/settings/Settings';
import Auth from './components/auth/Auth';
import ManageApplicants from './components/pages/ManageApplicants/ManageApplicants';
import UploadDocuments from './components/pages/UploadDocuments';
import Screening from './components/pages/Screening';
import StoryBuilder from './components/pages/StoryBuilder';

const App = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [currentView, setCurrentView] = useState('manageApplicants');
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

  const toggleMenu = () => {
    setMenuOpen(!isMenuOpen);
  };

  const setSelectedApplicantCustom = (newApplicant) => {
    if (!newApplicant && currentView !== Views.MANAGE_APPLICANTS) {
      changeView(Views.MANAGE_APPLICANTS);
    }
    setSelectedApplicant(newApplicant);
  };

  const changeView = (viewName) => {
    setCurrentView(viewName);
    toggleMenu();  // Close menu
  };

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
      case Views.UPLOAD_DOCUMENTS:
        return <UploadDocuments selectedApplicant={selectedApplicant} />;
      case Views.SCREENING:
        return <Screening selectedApplicant={selectedApplicant} />;
      case Views.STORY_BUILDER:
        return <StoryBuilder selectedApplicant={selectedApplicant} />;
      default:
        return <Text>Invalid View</Text>
    }
  };

  return (
    <VStack height="100%" width="100%">
      <Header toggleMenu={toggleMenu} onSettingsOpen={onOpen} />
      <MainMenu
        isOpen={isMenuOpen}
        onClose={toggleMenu}
        changeView={changeView}
        applicants={applicants}
        selectedApplicant={selectedApplicant}
        setSelectedApplicant={setSelectedApplicantCustom}
      />
      <Settings isOpen={isOpen} onClose={onClose} />
      {renderCurrentView()}
    </VStack>
  );
}

export default App;
