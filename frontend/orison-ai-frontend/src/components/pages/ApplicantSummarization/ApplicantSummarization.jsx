// ./components/pages/ApplicantSummarization/ApplicantSummarization.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import {
  collection, getDocs, orderBy, query, where, limit,
} from 'firebase/firestore';

// Chakra UI
import {
  Box, Button, HStack, Text, useToast, VStack, Spinner,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';

// Orison AI
import { summarize } from '../../../api/api';
import SummarizationDataDisplay from './SummarizationDataDisplay';

const ApplicantSummarization = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [summarizationDataStatus, setSummarizationDataStatus] = useState('');
  const [summarizationData, setSummarizationData] = useState(null);
  const [summarizationProgress, setSummarizationProgress] = useState('');
  const toast = useToast();

  const fetchSummarizationData = useCallback(async () => {
    if (user && selectedApplicant) {
      setSummarizationDataStatus('loading');
      const summarizationQuery = query(
        collection(db, "screening_builder"),
        where("attorney_id", "==", user.uid),
        where("applicant_id", "==", selectedApplicant.id),
        orderBy("date_created", "desc"),
        limit(1)
      );
      const querySnapshot = await getDocs(summarizationQuery);
      if (querySnapshot.empty) {
        setSummarizationData(null);
        setSummarizationDataStatus('not_found');
      } else {
        const data = querySnapshot.docs[0].data();
        setSummarizationData(data);
        setSummarizationDataStatus('found');
      }
    }
  }, [user, selectedApplicant]);

  useEffect(() => {
    fetchSummarizationData();
  }, [fetchSummarizationData, selectedApplicant]);

  const handleSummarize = async () => {
    if (selectedApplicant) {
      try {
        setSummarizationProgress('loading');
        await summarize(user.uid, selectedApplicant.id);
        setSummarizationProgress('success');
        toast({
          title: 'Summary Complete',
          description: `Summary generated successfully for ${selectedApplicant.name}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        await fetchSummarizationData();
      } catch (error) {
        setSummarizationProgress('error');
        toast({
          title: 'Summary Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  return (
    <VStack height="100%" width="100%" padding="16px">
      <HStack width="100%" mb="32px">
        <Text fontSize="32px" ml="16px" color="gray.400">Summary &gt;</Text>
        <Text fontSize="32px" color="green.300" as="strong">
          {selectedApplicant ? selectedApplicant.name : "None"}
        </Text>
      </HStack>
      <Box height="100%" width="80%" >
        <HStack width="100%" mb="20px" justifyContent="flex-start">
          <Button
            onClick={handleSummarize}
            colorScheme="green"
            isDisabled={summarizationProgress === 'loading'}
            mr="10px"
            mb="8px"
          >
            Generate Summary
          </Button>
          {summarizationProgress === 'loading' && (
            <Spinner color="blue.500" size="sm" />
          )}
          {summarizationProgress === 'success' && (
            <Box boxSize="24px">
              <CheckCircleIcon color="green.500" boxSize="100%" />
            </Box>
          )}
          {summarizationProgress === 'error' && (
            <Box boxSize="24px">
              <WarningIcon color="red.500" boxSize="100%" />
            </Box>
          )}
        </HStack>
        {summarizationDataStatus === 'found' && (
          <SummarizationDataDisplay data={summarizationData} />
        )}
        {summarizationDataStatus === 'loading' && (
          <Box bg="gray.900" p="20px" borderRadius="20px" width="60%" minWidth="600px">
            <Text>Loading summary data...</Text>
          </Box>
        )}
        {summarizationDataStatus === 'not_found' && (
          <Box bg="gray.900" p="20px" borderRadius="20px" width="60%" minWidth="600px">
            <Text>No summary data found.</Text>
          </Box>
        )}
      </Box>
    </VStack>
  );
};

export default ApplicantSummarization;