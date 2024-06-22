// ./components/pages/ApplicantDocuments/ApplicantDocuments.jsx

// React
import React from 'react';

// Chakra
import {
  HStack, VStack, Text,
} from '@chakra-ui/react';

// Orison
import ScholarLinkForm from './ScholarData/ScholarLinkForm';
import FileUploader from './ApplicantUploads/FileUploader';

const ApplicantDocuments = ({ selectedApplicant }) => (
  <VStack height="100%" width="100%" spacing={0} padding="16px" fontSize="32px">
    <HStack width="100%">
      <Text fontSize="32px" ml="16px" mb="32px" color="gray.400">Documents &gt;</Text>
      <Text fontSize="32px" mb="32px" color="green.300" as="strong">
        {selectedApplicant ? selectedApplicant.name : "None"}
      </Text>
    </HStack>
    <VStack width="70%" flex="1" pb="10px" overflowY="auto">
      <ScholarLinkForm selectedApplicant={selectedApplicant} />
      <FileUploader selectedApplicant={selectedApplicant} />
    </VStack>
  </VStack>
);

export default ApplicantDocuments;
