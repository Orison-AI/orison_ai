// ./App.jsx

// React
import React, { useEffect, useRef, useState } from 'react';

// Firebase
import { onAuthStateChanged } from "firebase/auth";

// Chakra
import {
  Box, Text, useDisclosure, VStack,
} from '@chakra-ui/react';

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
  const headerRef = useRef(null);
  const [headerHeight, setHeaderHeight] = useState(0);
  const navRef = useRef(null);
  const [navHeight, setNavHeight] = useState(0);
  const viewRef = useRef(null);

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
  
  useEffect(() => {
    const handleResize = () => {
      if (headerRef.current) {
        setHeaderHeight(headerRef.current.clientHeight);
      }
      if (navRef.current) {
        setNavHeight(navRef.current.clientHeight);
      }
    };
  
    handleResize(); // Call once on mount
    window.addEventListener('resize', handleResize); // Adjust on window resize
  
    return () => window.removeEventListener('resize', handleResize);
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
    <VStack className="oai-app" height="100vh" width="100vw" pb="20px">
      <Header
        ref={headerRef}
        goHome={() => setCurrentView(Views.MANAGE_APPLICANTS)}
        onSettingsOpen={onSettingsOpen}
      />
      <VStack className="oai-nav-and-view" height="100%" width="100%" padding="0 40px">
        <Navigation
          ref={navRef}
          applicants={applicants}
          selectedApplicant={selectedApplicant}
          setSelectedApplicant={setSelectedApplicant}
          currentView={currentView}
          setCurrentView={setCurrentView}
        />
        <Box
          className="oai-view"
          ref={viewRef}
          width="100%"
          flex="1"
          overflowY="auto"
          maxH={`calc(100vh - ${headerHeight}px - ${navHeight}px - 40px)`}
          pb="20px"
        >
          {renderCurrentView()}
        </Box>
      </VStack>
      <Settings isOpen={isSettingsOpen} onClose={onSettingsClose} />
    </VStack>
  );
}

export default App;
