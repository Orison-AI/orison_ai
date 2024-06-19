// ./components/settings/Settings.jsx

// React
import React from 'react';

// Firebase
import { signOut, deleteUser } from "firebase/auth";

// Chakra
import {
  Button, Center, // Box, HStack,
  Modal, ModalOverlay, ModalContent,
  Text, useToast, VStack
} from '@chakra-ui/react';

// Internal
import { auth } from '../../common/firebaseConfig';
// import ColorModeToggle from "../settings/ColorModeToggle";

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
            <Text fontSize="20px" mb="20px">
              Settings
            </Text>
            {/* Temporarily removing, since don't have time to support light mode
            <Box mb="10px">
              <ColorModeToggle />
            </Box>
            */}
            <Button colorScheme="blue" width="12vh" mb="10px" onClick={handleLogout}>Logout</Button>
            <Button colorScheme="red" width="12vh" mb="10px" onClick={handleDeleteAccount}>Delete Account</Button>
          </VStack>
        </Center>
      </ModalContent>
    </Modal>
  );
}

export default Settings;