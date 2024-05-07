// ./components/Header.jsx

import React from 'react';
import { Box, Center, HStack, IconButton, Icon } from '@chakra-ui/react';
import { HamburgerIcon, SettingsIcon } from '@chakra-ui/icons';

function Header({ toggleMenu, onSettingsOpen }) {
  return (
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
        onClick={onSettingsOpen} 
        variant="outline" 
      />
    </HStack>
  );
}

export default Header;
