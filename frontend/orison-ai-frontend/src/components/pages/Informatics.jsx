// ./components/pages/ApplicantInformatics.jsx

// External
import React from 'react';
import { Center, Text } from '@chakra-ui/react';

const ApplicantInformatics = ({selectedApplicant}) => {
  return (
    <Center height="100%" width="100%" padding="2vh" fontSize="4vh">
      Informatics: <Text ml="1vh" color="green.300" as="strong" display="inline">{selectedApplicant ? selectedApplicant.name : "No applicant selected"}</Text>
    </Center>
  );
}

export default ApplicantInformatics;
