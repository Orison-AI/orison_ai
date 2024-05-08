// ./components/pages/ManageApplicants/DeleteApplicantModal.jsx

import React from 'react';
import {
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text
} from '@chakra-ui/react';

const DeleteApplicantModal = ({ isOpen, onClose, onDelete, applicant }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Delete Applicant</ModalHeader>
        <ModalBody>
          <Text>
            Are you sure you want to delete <strong>{applicant}</strong>? This action cannot be undone.
          </Text>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="red" mr={3} onClick={onDelete}>
            Delete
          </Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default DeleteApplicantModal;
