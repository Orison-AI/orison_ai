// ./components/pages/UploadDocuments.jsx

// External
import React from 'react';
import { Center, Text } from '@chakra-ui/react';

const UploadDocuments = ({selectedApplicant}) => {
  return (
    <Center height="100%" width="100%" padding="2vh" fontSize="4vh">
      Upload Documents: <Text ml="1vh" color="green.300" as="strong" display="inline">{selectedApplicant ? selectedApplicant.name : "No applicant selected"}</Text>
    </Center>
  );
}

export default UploadDocuments;
