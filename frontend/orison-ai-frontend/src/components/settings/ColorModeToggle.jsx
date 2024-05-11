// ./ColorModeToggle.jsx

// React
import React from 'react';

// Chakra
import { useColorMode, Button, HStack } from '@chakra-ui/react';

const ColorModeToggle = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <HStack width="20vh" spacing={0}>
      <Button
        onClick={toggleColorMode}
        isDisabled={colorMode === 'light'}
        colorScheme="blue"
        borderRadius="0px"
        borderTopLeftRadius="8px"
        borderBottomLeftRadius="8px"
      >
        Light
      </Button>
      <Button
        onClick={toggleColorMode}
        isDisabled={colorMode === 'dark'}
        colorScheme="blue"
        borderRadius="0"
        borderTopRightRadius="8px"
        borderBottomRightRadius="8px"
      >
        Dark
      </Button>
    </HStack>
  );
};

export default ColorModeToggle;
