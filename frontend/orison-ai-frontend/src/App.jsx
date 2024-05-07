// ./App.jsx

// External
import React, { useState } from 'react';
import { 
  Box, Center, HStack, IconButton, Icon,
  useDisclosure, VStack,
} from '@chakra-ui/react';
import { HamburgerIcon, SettingsIcon } from '@chakra-ui/icons';

// Internal
import MainMenu from './pages/MainMenu';
import Settings from './pages/Settings';

const App = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const toggleMenu = () => {
    setMenuOpen(!isMenuOpen);
  };

  return (
    <VStack height="100%" width="100%" padding="2vh">
      <HStack width="100%">
        <IconButton 
          aria-label="Open menu" 
          icon={<Icon as={HamburgerIcon} />} 
          onClick={toggleMenu} 
          variant="outline" 
        />
        <Center width="100%">
          <Box fontSize="3vh">orison.ai</Box>
        </Center>
        <IconButton 
          aria-label="Open settings" 
          icon={<Icon as={SettingsIcon} />}
          onClick={onOpen} 
          variant="outline" 
        />
      </HStack>
      <MainMenu isOpen={isMenuOpen} onClose={toggleMenu} />
      <Settings isOpen={isOpen} onClose={onClose} />
    </VStack>
  );
}

export default App;
