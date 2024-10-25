// ./components/Header.jsx

// React
import React from 'react';

// Chakra
import {
  Box, Center, HStack, IconButton, useColorModeValue, Spacer,
} from '@chakra-ui/react';
import { SettingsIcon } from '@chakra-ui/icons';
import { AiFillHome, AiFillEdit } from 'react-icons/ai';

// Internal
import ColorModeToggle from './settings/ColorModeToggle';

const Header = React.forwardRef(({ goHome, editQuestionaire, onSettingsOpen }, ref) => {
  const headerColor = useColorModeValue("rgba(23, 25, 35, 0.10)", "rgba(23, 25, 35, 0.90)");

  return (
    <HStack className="oai-header" ref={ref} width="100%" bg={headerColor} p="8px" pl="16px" pr="16px" alignItems="center">
      {/* Home Button */}
      <IconButton
        aria-label="Home"
        icon={<AiFillHome />}
        onClick={goHome}
      />

      {/* Edit Questionnaire Button */}
      <IconButton
        aria-label="EditQuestionaire"
        icon={<AiFillEdit />}
        onClick={editQuestionaire}
      />

      {/* Title in the Center */}
      <Center width="100%">
        <Box fontSize="32px">void pointer.ai</Box>
      </Center>

      {/* Color Mode Toggle */}
      <ColorModeToggle />

      {/* Settings Button */}
      <IconButton
        aria-label="Open settings"
        icon={<SettingsIcon />}
        onClick={onSettingsOpen}
      />
    </HStack>
  );
});

export default Header;
