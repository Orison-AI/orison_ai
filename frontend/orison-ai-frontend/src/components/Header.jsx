// ./components/Header.jsx

// React
import React from 'react';

// Chakra
import {
  Box, Center, HStack, IconButton, useColorModeValue,
} from '@chakra-ui/react';
import { SettingsIcon } from '@chakra-ui/icons';
import { AiFillHome, AiFillEdit, AiOutlineAppstore } from 'react-icons/ai';

// Internal
import ColorModeToggle from './settings/ColorModeToggle';

const Header = React.forwardRef(({ goHome, onSettingsOpen, landingPage }, ref) => {
  const headerColor = useColorModeValue("rgba(23, 25, 35, 0.10)", "rgba(23, 25, 35, 0.90)");

  return (
    <HStack className="oai-header" ref={ref} width="100%" bg={headerColor} p="10px" pl="16px" pr="16px" alignItems="center">
      {/* Application Home Button */}
      <IconButton
        aria-label="Application Home"
        icon={<AiFillHome />}
        onClick={goHome}
      />

      {/* Title in the Center */}
      <Box
        position="absolute"
        left="50%"
        transform="translateX(-50%)"
        fontSize="32px"
        fontWeight="bold"
      >
        Orison AI
      </Box>

      {/* Color Mode Toggle */}
      {/* <ColorModeToggle /> */}

      {/* Settings Button */}
      <IconButton
        aria-label="Open settings"
        icon={<SettingsIcon />}
        onClick={onSettingsOpen}
      />

      {/* Home Button (Website Homepage) */}
      <IconButton
        aria-label="Website Home"
        icon={<AiOutlineAppstore />}
        onClick={landingPage}
        ml="auto"
      />
    </HStack>
  );
});

export default Header;
