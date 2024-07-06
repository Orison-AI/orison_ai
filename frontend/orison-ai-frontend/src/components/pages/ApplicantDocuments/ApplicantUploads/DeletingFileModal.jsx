// ./components/pages/ApplicantDocuments/ApplicantUploads/DeletingFileModal.jsx

// React
import React from 'react';

// Chakra
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text, Spinner
} from '@chakra-ui/react';

const DeletingFileModal = ({ isOpen, onClose, fileName }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Deleting File</ModalHeader>
        <ModalBody>
          <Spinner size="xl" />
          <Text mt={4}>
            The file <strong>{fileName}</strong> is currently being deleted. Please wait until the deletion is complete.
          </Text>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default DeletingFileModal;
