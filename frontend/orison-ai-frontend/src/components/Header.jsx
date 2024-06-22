// ./components/Header.jsx

// React
import React from 'react';

// Chakra
import {
  Box, Center, HStack, Icon, IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { HamburgerIcon, SettingsIcon } from '@chakra-ui/icons';

function Header({ toggleMenu, onSettingsOpen }) {
  const headerColor = useColorModeValue("rgba(23, 25, 35, 0.10)", "rgba(23, 25, 35, 0.90)");

  return (
    <HStack width="100%" bg={headerColor} p="8px" pl="16px" pr="16px">
      <IconButton 
        aria-label="Open menu" 
        icon={<Icon as={HamburgerIcon} />} 
        onClick={toggleMenu} 
        variant="outline" 
      />
      <Center width="100%">
        <Box fontSize="32px">orison.ai</Box>
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
