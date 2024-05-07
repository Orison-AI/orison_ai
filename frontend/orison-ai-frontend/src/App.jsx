// ./App.jsx

// External
import React, { useState } from 'react';
import { useDisclosure, VStack } from '@chakra-ui/react';

// Internal
import MainMenu from './components/MainMenu';
import Header from './components/Header';
import Settings from './components/Settings';
import SelectApplicant from './components/pages/SelectApplicant';
import UploadDocuments from './components/pages/UploadDocuments';
import InitialEvaluation from './components/pages/InitialEvaluation';
import DetailedEvaluation from './components/pages/DetailedEvaluation';

const App = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [currentView, setCurrentView] = useState('selectApplicant');

  const toggleMenu = () => {
    setMenuOpen(!isMenuOpen);
  };

  const changeView = (viewName) => {
    setCurrentView(viewName);
    toggleMenu();  // Close menu
  };

  const renderCurrentView = () => {
    switch(currentView) {
      case 'selectApplicant':
        return <SelectApplicant />;
      case 'uploadDocuments':
        return <UploadDocuments />;
      case 'initialEvaluation':
        return <InitialEvaluation />;
      case 'detailedEvaluation':
        return <DetailedEvaluation />;
      default:
        return <SelectApplicant />; // Default case
    }
  };

  return (
    <VStack height="100%" width="100%" padding="2vh">
      <Header toggleMenu={toggleMenu} onSettingsOpen={onOpen} />
      <MainMenu isOpen={isMenuOpen} onClose={toggleMenu} changeView={changeView} />
      <Settings isOpen={isOpen} onClose={onClose} />
      {renderCurrentView()}
    </VStack>
  );
}

export default App;
