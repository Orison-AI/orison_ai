// ./components/pages/ApplicantDocuments/ApplicantUploads/ViewFileModal.jsx

// React
import React from 'react';

// Chakra UI
import {
  Box, Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text,
} from '@chakra-ui/react';

const ViewFileModal = ({ isOpen, onClose, fileName, fileContent }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="3xl">
      <ModalOverlay />
      <ModalContent p="20px">
        <ModalHeader fontSize="2xl">{fileName}</ModalHeader>
        <ModalBody>
          <Box whiteSpace="pre-wrap" bg="gray.900" p="20px" borderRadius="8px">
            <Text>{fileContent}</Text>
          </Box>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ViewFileModal;
