// ./components/MainMenu.jsx

import React from 'react';
import {
  Button,
  Drawer, DrawerOverlay, DrawerContent,
  DrawerCloseButton, DrawerHeader, DrawerBody,
  useColorMode, VStack,
} from '@chakra-ui/react';

function MainMenu({ isOpen, onClose }) {

  const { colorMode } = useColorMode();
  const buttonHoverColor = colorMode === "light" ? "gray.100" : "gray.600";

  const MenuButton = ({label}) => (
    <Button 
      variant="ghost"
      width="100%"
      justifyContent="flex-start"
      _hover={{ bg: buttonHoverColor }}
    >
      {label}
    </Button>
  );

  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="left">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>orison.ai</DrawerHeader>
        <DrawerBody pl="4vh">
          <VStack spacing={4}>
            <MenuButton label="Select Applicant" />
            <MenuButton label="Upload Documents" />
            <MenuButton label="Initial Evaluation" />
            <MenuButton label="Detailed Evaluation" />
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
