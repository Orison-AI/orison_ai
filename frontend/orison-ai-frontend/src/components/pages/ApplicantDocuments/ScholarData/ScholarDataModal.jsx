// ./components/pages/Documents/ScholarDataModal.jsx

// React
import React from 'react';

// Chakra UI
import {
  Box, Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button,
} from '@chakra-ui/react';

// Orison AI
import StructuredData from '../../../StructuredData';

const ScholarDataModal = ({ isOpen, onClose, data }) => {
  const keys = [
    { key: "author", collapsible: true, subKeys: [
        { key: "name" },
        { key: "affiliation" },
        { key: "scholar_id" },
        { key: "profile_link" },
      ]
    },
    { key: "keywords", collapsible: true, dynamic: true },
    { key: "homepage" },
    { key: "h_index" },
    { key: "h_index_5y" },
    { key: "cited_by" },
    { key: "cited_by_5y" },
    { key: "cited_each_year", collapsible: true, dynamic: true },
    { key: "co_authors", collapsible: true, dynamic: true, dynamic_collapsible: true, subKeys: [
        { key: "name" },
        { key: "affiliation" },
        { key: "scholar_id" },
      ]
    },
    { key: "publications", collapsible: true, dynamic: true, dynamic_collapsible: true, subKeys: [
        { key: "authors" },
        { key: "title" },
        { key: "year" },
        { key: "type_of_paper" },
        { key: "cited_by" },
        { key: "peer_reviews" },
      ]
    },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="3xl">
      <ModalOverlay />
      <ModalContent p="20px">
        <ModalHeader fontSize="2xl">Scholar Data</ModalHeader>
        <ModalBody>
          <Box>
            <StructuredData data={data} keys={keys} />
          </Box>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ScholarDataModal;
