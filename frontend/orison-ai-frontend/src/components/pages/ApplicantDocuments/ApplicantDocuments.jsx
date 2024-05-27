// ./components/pages/Documents/ApplicantDocuments.jsx

// React
import React from 'react';

// Chakra
import {
  HStack, VStack, Text,
} from '@chakra-ui/react';

// Orison
import ScholarLinkForm from './ScholarLinkForm';
import FileUploader from './FileUploader';

const ApplicantDocuments = ({ selectedApplicant }) => (
  <VStack height="100%" width="100%" padding="2vh" fontSize="4vh">
    <HStack width="100%">
      <Text fontSize="32px" ml="2vh" mb="4vh" color="gray.400">Documents &gt;</Text>
      <Text fontSize="32px" mb="4vh" color="green.300" as="strong">
        {selectedApplicant ? selectedApplicant.name : "None"}
      </Text>
    </HStack>
    <ScholarLinkForm selectedApplicant={selectedApplicant} />
    <FileUploader selectedApplicant={selectedApplicant} />
  </VStack>
);

export default ApplicantDocuments;
