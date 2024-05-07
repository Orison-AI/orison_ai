// ./App.jsx

// External
import React, { useState } from 'react';
import { useDisclosure, VStack } from '@chakra-ui/react';

// Internal
import MainMenu from './components/MainMenu';
import Header from './components/Header';
import Settings from './components/Settings';

const App = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const toggleMenu = () => {
    setMenuOpen(!isMenuOpen);
  };

  return (
    <VStack height="100%" width="100%" padding="2vh">
      <Header toggleMenu={toggleMenu} onSettingsOpen={onOpen} />
      <MainMenu isOpen={isMenuOpen} onClose={toggleMenu} />
      <Settings isOpen={isOpen} onClose={onClose} />
    </VStack>
  );
}

export default App;
