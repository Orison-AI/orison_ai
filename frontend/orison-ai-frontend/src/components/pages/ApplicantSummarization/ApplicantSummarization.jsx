// ./components/pages/ApplicantSummarization/ApplicantSummarization.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import { collection, getDocs, orderBy, query, where, limit } from 'firebase/firestore';

// Chakra UI
import {
  HStack, VStack, Text, Button, useToast,
} from '@chakra-ui/react';

// Orison AI
import { summarize } from '../../../api/api';
import SummarizationDataDisplay from './SummarizationDataDisplay';


const ApplicantSummarization = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [summarizationDataStatus, setSummarizationDataStatus] = useState('');
  const [summarizationData, setSummarizationData] = useState(null);
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
    <VStack height="100%" width="100%" padding="2vh">
      <HStack width="100%" mb="4vh">
        <Text fontSize="32px" ml="2vh" color="gray.400">Summarization &gt;</Text>
        <Text fontSize="32px" color="green.300" as="strong">
          {selectedApplicant ? selectedApplicant.name : "None"}
        </Text>
      </HStack>
      <Button onClick={handleSummarize} colorScheme="green">
        Summarize
      </Button>
      {summarizationDataStatus === 'found' && (
        <SummarizationDataDisplay data={summarizationData} />
      )}
      {summarizationDataStatus === 'loading' && (
        <Text>Loading summarization data...</Text>
      )}
      {summarizationDataStatus === 'not_found' && (
        <Text>No summarization data found.</Text>
      )}
    </VStack>
  );
};

export default ApplicantSummarization;
