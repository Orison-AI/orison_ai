// ./components/pages/Documents/ScholarDataModal.jsx

// React
import React from 'react';

// Chakra UI
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button,
} from '@chakra-ui/react';

// Orison AI
import StructuredData from './StructuredData';

const ScholarDataModal = ({ isOpen, onClose, data }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Scholar Data</ModalHeader>
        <ModalBody>
          <StructuredData data={data} />
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ScholarDataModal;
