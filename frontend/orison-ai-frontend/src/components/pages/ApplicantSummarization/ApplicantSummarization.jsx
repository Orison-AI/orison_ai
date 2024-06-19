// ./components/pages/ApplicantSummarization/ApplicantSummarization.jsx

// React
import React from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../common/firebaseConfig';

// Chakra
import {
  HStack, VStack, Text, Button, useToast,
} from '@chakra-ui/react';

// Orison
import { summarize } from '../../../api/api';

const ApplicantSummarization = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const toast = useToast();

  const handleSummarize = async () => {
    if (selectedApplicant) {
      try {
        const response = await summarize(user.uid, selectedApplicant.id);
        toast({
          title: 'Summarization Started',
          description: `Summarization for ${selectedApplicant.name} has started. Request ID: ${response.requestId}`,
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
      } catch (error) {
        toast({
          title: 'Summarization Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  return (
    <VStack height="100%" width="100%" padding="2vh" fontSize="4vh">
      <HStack width="100%" mb="4vh">
        <Text fontSize="32px" ml="2vh" color="gray.400">Informatics &gt;</Text>
        <Text fontSize="32px" color="green.300" as="strong">
          {selectedApplicant ? selectedApplicant.name : "None"}
        </Text>
      </HStack>
      <Button onClick={handleSummarize} colorScheme="green">
        Summarize
      </Button>
    </VStack>
  );
};

export default ApplicantSummarization;
