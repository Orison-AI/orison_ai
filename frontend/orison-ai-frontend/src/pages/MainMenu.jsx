// src/MainMenu.jsx

import React from 'react';
import { Drawer, DrawerOverlay, DrawerContent, DrawerCloseButton, DrawerHeader, DrawerBody, VStack, Link } from '@chakra-ui/react';

function MainMenu({ isOpen, onClose }) {
  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="left">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>Menu</DrawerHeader>
        <DrawerBody>
          <VStack spacing={4}>
            <Link href="#">Option 1</Link>
            <Link href="#">Option 2</Link>
            <Link href="#">Option 3</Link>
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
