// ./components/pages/ApplicantDocuments/ApplicantUploads/DeleteFileModal.jsx

// React
import React from 'react';

// Chakra
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text
} from '@chakra-ui/react';

const DeleteFileModal = ({ isOpen, onClose, onConfirm, fileName }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Delete File</ModalHeader>
        <ModalBody>
          <Text>
            Are you sure you want to delete the file <strong>{fileName}</strong>? This action cannot be undone.
          </Text>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="red" mr={3} onClick={onConfirm}>
            Delete
          </Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default DeleteFileModal;
