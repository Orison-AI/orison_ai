// ./components/pages/ApplicantDocuments/ApplicantDocuments.jsx

// React
import React from 'react';

// Chakra
import { VStack } from '@chakra-ui/react';

// Orison
import ScholarLinkForm from './ScholarData/ScholarLinkForm';
import FileUploader from './ApplicantUploads/FileUploader';

const ApplicantDocuments = ({ selectedApplicant }) => {
  return (
    <VStack height="100%" width="100%" spacing={0} padding="16px" fontSize="32px">
      <VStack width="70%" flex="1" pb="10px" overflowY="auto">
        <ScholarLinkForm selectedApplicant={selectedApplicant} />
        <FileUploader selectedApplicant={selectedApplicant} />
      </VStack>
    </VStack>
  );
};

export default ApplicantDocuments;
