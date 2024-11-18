// React
import React from 'react';

// Firebase
import { signOut, deleteUser } from "firebase/auth";
import { doc, deleteDoc } from "firebase/firestore";  // Add Firestore imports

// Chakra
import {
  Button, Center, Modal, ModalOverlay, ModalContent,
  Text, useToast, VStack
} from '@chakra-ui/react';

// Internal
import { auth, db } from '../../common/firebaseConfig';  // Ensure Firestore (db) is imported
import { useApplicantContext } from '../../context/ApplicantContext';

function Settings({ isOpen, onClose }) {
  const toast = useToast();
  const user = auth.currentUser;  // Get the current user for account deletion
  const { selectedApplicant } = useApplicantContext();

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

  const handleDeleteAccount = async ({ }) => {
    try {
      if (user) {
        // Step 1: Delete the attorney's document from Firestore
        const attorneyDocRef = doc(db, "templates", selectedApplicant.id);
        await deleteDoc(attorneyDocRef);
        console.log("Attorney data deleted from Firestore.");

        // Step 2: Delete the user account from Firebase Auth
        await deleteUser(user);
        console.log("User account deleted from Firebase Auth.");

        toast({
          title: "Account deleted",
          description: "Your account has been successfully deleted.",
          status: "success",
          duration: 5000,
          isClosable: true
        });

        onClose();
      }
    } catch (error) {
      console.error("Error deleting account or data:", error);
      toast({
        title: "Deletion failed",
        description: error.message,
        status: "error",
        duration: 5000,
        isClosable: true
      });
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <Center width="100%" p="8px">
          <VStack width="100%">
            <Text fontSize="20px" mb="20px">
              Settings
            </Text>
            <Button colorScheme="blue" width="116px" mb="10px" onClick={handleLogout}>Logout</Button>
            <Button colorScheme="red" width="116px" mb="10px" onClick={handleDeleteAccount}>Delete Account</Button>
          </VStack>
        </Center>
      </ModalContent>
    </Modal>
  );
}

export default Settings;
