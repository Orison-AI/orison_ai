// ./App.jsx

import React, { useEffect, useRef, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { Box, Text, useDisclosure, Flex } from "@chakra-ui/react";

import { auth } from "./common/firebaseConfig";
import ApplicantDocuments from "./components/pages/ApplicantDocuments/ApplicantDocuments";
import ApplicantSummarization from "./components/pages/ApplicantSummarization/ApplicantSummarization";
import Evidence from "./components/pages/EvidenceLetter/evidence";
import DocAssist from "./components/pages/DocAssist/DocAssist";
import Auth from "./components/auth/Auth";
import Header from "./components/Header";
import QuestionaireEditor from "./components/pages/QuestionaireEditor/QuestionaireEditor";
import ManageApplicants from "./components/pages/ManageApplicants/ManageApplicants";
import Navigation from "./components/Navigation";
import Settings from "./components/settings/Settings";
import Views from "./common/views";
import { ApplicantProvider, useApplicantContext } from "./context/ApplicantContext";

const AppContent = () => {
  const [user, setUser] = useState(null);
  const { isOpen: isSettingsOpen, onOpen: onSettingsOpen, onClose: onSettingsClose } = useDisclosure();
  const [currentView, setCurrentView] = useState(Views.MANAGE_APPLICANTS);
  const [applicants, setApplicants] = useState([]);
  const { selectedApplicant, setSelectedApplicant } = useApplicantContext();

  const headerRef = useRef(null);
  const [headerHeight, setHeaderHeight] = useState(0);
  const navRef = useRef(null);
  const [navHeight, setNavHeight] = useState(0);
  const viewRef = useRef(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        setUser(null);
      }
    });

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

    handleResize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!user) {
    return <Auth />;
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case Views.MANAGE_APPLICANTS:
        return (
          <ManageApplicants
            applicants={applicants}
            setApplicants={setApplicants}
            selectedApplicant={selectedApplicant}
            setSelectedApplicant={setSelectedApplicant}
            setCurrentView={setCurrentView}
          />
        );
      case Views.QUESTIONAIRE:
        return <QuestionaireEditor selectedApplicant={selectedApplicant} />;
      case Views.APPLICANT_DOCUMENTS:
        return <ApplicantDocuments selectedApplicant={selectedApplicant} />;
      case Views.APPLICANT_SUMMARIZATION:
        return <ApplicantSummarization selectedApplicant={selectedApplicant} />;
      case Views.DOCASSIST:
        return <DocAssist selectedApplicant={selectedApplicant} />;
      case Views.EVIDENCE:
        return <Evidence selectedApplicant={selectedApplicant} />;
      default:
        return <Text>Invalid View</Text>;
    }
  };

  return (
    <Flex className="oai-app" direction="column" height="100vh" width="100vw">
      <Header
        ref={headerRef}
        goHome={() => setCurrentView(Views.MANAGE_APPLICANTS)}
        landingPage={() => (window.location.href = "https://orison.ai")}
        onSettingsOpen={onSettingsOpen}
      />
      <Flex className="oai-nav-and-view" direction="column" flex="1" width="100%" padding="0 40px" overflow="hidden">
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
          maxHeight={`calc(100vh - ${headerHeight}px - ${navHeight}px)`}
        >
          {renderCurrentView()}
        </Box>
        {/* Global Footer (Footnote) */}
        <Box
          className="footnote"
          textAlign="center"
          fontSize="sm"
          color="gray.400"
          borderTop="1px solid"
          borderColor="gray.700"
          padding="10px"
          bg="gray.900"
        >
          © 2024 Orison AI. All rights reserved. AI can make mistakes. Please verify the information.
        </Box>
      </Flex>
      <Settings isOpen={isSettingsOpen} onClose={onSettingsClose} />
    </Flex>
  );
};

const App = () => (
  <ApplicantProvider>
    <AppContent />
  </ApplicantProvider>
);

export default App;
