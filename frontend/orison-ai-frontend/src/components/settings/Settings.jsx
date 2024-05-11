// ./components/settings/Settings.jsx

// React
import React from 'react';

// Chakra
import {
  Center, Modal, ModalOverlay, ModalContent, Text, VStack,
} from '@chakra-ui/react';

// Internal
import ColorModeToggle from "../settings/ColorModeToggle";

function Settings({ isOpen, onClose }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <Center width="100%" p="1vh">
          <VStack width="100%">
            <Text fontSize="2vh" mb="4vh">
              Settings
            </Text>
            <ColorModeToggle />
          </VStack>
        </Center>
      </ModalContent>
    </Modal>
  );
}

export default Settings;