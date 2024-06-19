// ./components/pages/ApplicantDocuments/FileContentModal.jsx

// React
import React from 'react';

// Chakra UI
import {
  Box, Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text,
} from '@chakra-ui/react';

const FileContentModal = ({ isOpen, onClose, fileName, fileContent }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="3xl">
      <ModalOverlay />
      <ModalContent p="20px">
        <ModalHeader fontSize="2xl">{fileName}</ModalHeader>
        <ModalBody>
          <Box whiteSpace="pre-wrap">
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

export default FileContentModal;
