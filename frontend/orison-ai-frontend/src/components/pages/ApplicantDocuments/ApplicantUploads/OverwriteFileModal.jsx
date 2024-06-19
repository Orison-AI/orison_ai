// ./components/pages/ApplicantDocuments/ApplicantUploads/OverwriteFileModal.jsx

// React
import React from 'react';

// Chakra
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text
} from '@chakra-ui/react';

const OverwriteFileModal = ({ isOpen, onClose, onConfirm, fileName }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Overwrite File</ModalHeader>
        <ModalBody>
          <Text>
            The file <strong>{fileName}</strong> already exists. Do you want to overwrite it? This action cannot be undone.
          </Text>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="red" mr={3} onClick={onConfirm}>
            Overwrite
          </Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default OverwriteFileModal;
