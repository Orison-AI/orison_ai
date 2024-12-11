// ./components/pages/ApplicantDocuments/ApplicantDocuments.jsx

// React
import React from 'react';

// Chakra
import { Center, VStack } from '@chakra-ui/react';

// Orison
import ScholarLinkForm from './ScholarData/ScholarLinkForm';
import FileUploader from './ApplicantUploads/FileUploader';
import { useApplicantContext } from '../../../context/ApplicantContext';

const ApplicantDocuments = ({ }) => {
  const { selectedApplicant } = useApplicantContext();

  return (
    <Center className="oai-appdocs-center" width="100%" flex="1">
      <VStack className="oai-appdocs-stack" width="70%">
        <FileUploader selectedApplicant={selectedApplicant} />
      </VStack>
    </Center>
  );
};

export default ApplicantDocuments;
