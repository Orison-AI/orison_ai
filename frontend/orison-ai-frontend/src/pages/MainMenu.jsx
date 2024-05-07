// src/MainMenu.jsx

import React from 'react';
import {
  Button, Center,
  Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton,
  DrawerHeader, DrawerFooter, DrawerBody,
  Link, useColorMode, VStack,
} from '@chakra-ui/react';

function MainMenu({ isOpen, onClose }) {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="left">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>orison.ai</DrawerHeader>
        <DrawerBody>
          <VStack spacing={4}>
            <Link href="#">Select Applicant</Link>
            <Link href="#">Upload Documents</Link>
            <Link href="#">Initial Evaluation</Link>
            <Link href="#">Detailed Evaluation</Link>
          </VStack>
        </DrawerBody>
        <DrawerFooter>
          <Center width="100%">
            <Button onClick={toggleColorMode}>
              Color Mode: {colorMode === 'light' ? 'Light' : 'Dark'}
            </Button>
          </Center>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
