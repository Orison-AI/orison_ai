// ./components/MainMenu.jsx

import React from 'react';
import {
  Button,
  Drawer, DrawerOverlay, DrawerContent,
  DrawerCloseButton, DrawerHeader, DrawerBody,
  useColorMode, VStack,
} from '@chakra-ui/react';

function MainMenu({ isOpen, onClose, changeView }) {

  const { colorMode } = useColorMode();
  const buttonHoverColor = colorMode === "light" ? "gray.100" : "gray.600";

  const MenuButton = ({label, onClick}) => (
    <Button 
      variant="ghost"
      width="100%"
      justifyContent="flex-start"
      onClick={onClick}
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
            <MenuButton label="Select Applicant" onClick={() => changeView('selectApplicant')} />
            <MenuButton label="Upload Documents" onClick={() => changeView('uploadDocuments')} />
            <MenuButton label="Initial Evaluation" onClick={() => changeView('initialEvaluation')} />
            <MenuButton label="Detailed Evaluation" onClick={() => changeView('detailedEvaluation')} />
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
