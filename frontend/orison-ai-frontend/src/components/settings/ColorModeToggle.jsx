// ./ColorModeToggle.jsx

// React
import React from 'react';

// Chakra
import {
  Button, Center, useColorMode,
} from '@chakra-ui/react';

const ColorModeToggle = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Center width="160px">
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
    </Center>
  );
};

export default ColorModeToggle;
