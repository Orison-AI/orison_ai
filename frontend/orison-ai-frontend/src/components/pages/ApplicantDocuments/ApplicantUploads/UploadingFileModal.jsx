// ./components/pages/ApplicantDocuments/ApplicantUploads/UploadingFileModal.jsx

// React
import React from 'react';

// Chakra
import {
  Button, Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Spinner, Text,
} from '@chakra-ui/react';

const UploadingFileModal = ({ isOpen, onClose, fileName }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Uploading File</ModalHeader>
        <ModalBody>
          <Spinner size="xl" />
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
