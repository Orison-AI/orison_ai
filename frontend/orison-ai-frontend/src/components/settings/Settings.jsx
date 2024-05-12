// ./components/settings/Settings.jsx

// React
import React from 'react';

// Firebase
import { signOut, deleteUser } from "firebase/auth";

// Chakra
import {
  Box, Button, Center, HStack,
  Modal, ModalOverlay, ModalContent,
  Text, useToast, VStack
} from '@chakra-ui/react';

// Internal
import { auth } from '../../firebaseConfig';
import ColorModeToggle from "../settings/ColorModeToggle";

function Settings({ isOpen, onClose }) {
  const toast = useToast();

  const handleLogout = () => {
    signOut(auth).then(() => {
      toast({
        title: "Logged out",
        description: "You have been successfully logged out.",
        status: "success",
        duration: 5000,
        isClosable: true
      });
      onClose();
    }).catch((error) => {
      toast({
        title: "Logout failed",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true
      });
    });
  };

  const handleDeleteAccount = () => {
    deleteUser(auth.currentUser).then(() => {
      toast({
        title: "Account deleted",
        description: "Your account has been successfully deleted.",
        status: "success",
        duration: 5000,
        isClosable: true
      });
      onClose();
    }).catch((error) => {
      toast({
        title: "Deletion failed",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true
      });
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <Center width="100%" p="1vh">
          <VStack width="100%">
            <Text fontSize="2vh">
              Settings
            </Text>
            <Text fontSize="1vh" mb="4vh">
              (in progress)
            </Text>
            <Box mb="1vh">
              <ColorModeToggle />
            </Box>
            <HStack mb="1vh">
              <Button colorScheme="blue" width="12vh" onClick={handleLogout}>Logout</Button>
              <Button colorScheme="red" width="12vh" onClick={handleDeleteAccount}>Delete Account</Button>
            </HStack>
          </VStack>
        </Center>
      </ModalContent>
    </Modal>
  );
}

export default Settings;