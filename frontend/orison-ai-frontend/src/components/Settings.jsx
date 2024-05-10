// ./components/Settings.jsx

import React from 'react';
import {
  Button, Center,
  Modal, ModalOverlay, ModalContent,
  useColorMode,
} from '@chakra-ui/react';

function Settings({ isOpen, onClose }) {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <Center width="100%" p="1vh" fontSize="2vh">
          Settings
        </Center>
        <Center width="100%" p="1vh">
          <Button onClick={toggleColorMode}>
            Color Mode: {colorMode === 'light' ? 'Light' : 'Dark'}
          </Button>
        </Center>
      </ModalContent>
    </Modal>
  );
}

export default Settings;