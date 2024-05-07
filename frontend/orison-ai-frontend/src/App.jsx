// ./App.jsx

// External
import React, { useState } from 'react';
import { 
  Box, Center, HStack, IconButton, Icon, VStack,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';

// Internal
import MainMenu from './pages/MainMenu';

const App = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);

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
      </HStack>
      <MainMenu isOpen={isMenuOpen} onClose={toggleMenu} />
    </VStack>
  );
}

export default App;
