// ./components/pages/ApplicantDocuments/ApplicantUploads/UploadingFileModal.jsx

// React
import React from 'react';

// Chakra
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text
} from '@chakra-ui/react';

const UploadingFileModal = ({ isOpen, onClose, fileName }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Uploading File</ModalHeader>
        <ModalBody>
          <Text>
            The file <strong>{fileName}</strong> is currently being uploaded. Please wait until the upload is complete.
          </Text>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default UploadingFileModal;
