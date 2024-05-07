// ./pages/MainMenu.jsx

import React from 'react';
import {
  Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton,
  DrawerHeader, DrawerBody,
  Link, VStack,
} from '@chakra-ui/react';

function MainMenu({ isOpen, onClose }) {
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
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
