// ./components/pages/ApplicantInformatics.jsx

// React
import React from 'react';

// Chakra
import {
  HStack, VStack, Text,
} from '@chakra-ui/react';

const ApplicantInformatics = ({ selectedApplicant }) => (
  <VStack height="100%" width="100%" padding="2vh" fontSize="4vh">
    <HStack width="100%">
      <Text fontSize="3vh" ml="2vh" mb="4vh" color="gray.400">Informatics &gt;</Text>
      <Text fontSize="3vh" mb="4vh" color="green.300" as="strong">
        {selectedApplicant ? selectedApplicant.name : "None"}
      </Text>
    </HStack>
  </VStack>
);

export default ApplicantInformatics;
