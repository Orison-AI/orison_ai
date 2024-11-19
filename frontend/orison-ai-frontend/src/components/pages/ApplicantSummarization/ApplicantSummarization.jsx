import React, { useCallback, useEffect, useState } from 'react';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import {
  collection, getDocs, orderBy, query, limit, doc,
} from 'firebase/firestore';
import {
  Box, Button, Center, HStack, Text, useToast, VStack, Spinner,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';
import { summarize } from '../../../api/api';
import SummarizationDataDisplay from './SummarizationDataDisplay';
import { useApplicantContext } from '../../../context/ApplicantContext';

const ApplicantSummarization = () => {
  const [user] = useAuthState(auth);
  const [summarizationDataStatus, setSummarizationDataStatus] = useState('');
  const [summarizationData, setSummarizationData] = useState(null);
  const [summarizationProgress, setSummarizationProgress] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const toast = useToast();
  const { selectedApplicant } = useApplicantContext();

  const fetchSummarizationData = useCallback(async () => {
    if (user && selectedApplicant) {
      setSummarizationDataStatus('loading');
      const summarizationQuery = query(
        collection(doc(collection(db, "screening_builder"), user.uid), selectedApplicant.id),
        orderBy("date_created", "desc"),
        limit(1)
      );
      const querySnapshot = await getDocs(summarizationQuery);
      if (querySnapshot.empty) {
        setSummarizationData(null);
        setSummarizationDataStatus('not_found');
        setLastUpdated(''); // Reset timestamp when no data is found
      } else {
        const data = querySnapshot.docs[0].data();
        setSummarizationData(data);
        setSummarizationDataStatus('found');
        // Update the last updated timestamp
        const timestamp = data.date_created.toDate(); // Firestore timestamp to JS Date
        setLastUpdated(new Intl.DateTimeFormat('en-US', {
          dateStyle: 'medium',
          timeStyle: 'short',
        }).format(timestamp));
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
    <Box className="oai-appsum" height="100%" width="100%" >
      <Center width="100%" flex="1">
        <VStack height="100%" width="100%">
          <HStack className="oai-appsum-generate-stack" mb="20px" justifyContent="flex-start">
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
            <>
              <Text fontSize="sm" color="gray.500">
                Last Updated: {lastUpdated}
              </Text>
              <SummarizationDataDisplay data={summarizationData} />
            </>
          )}
          {summarizationDataStatus === 'loading' && (
            <Box className="oai-appsum-loading" bg="gray.900" p="20px" borderRadius="20px" width="60%" minWidth="600px">
              <Text>Loading summary data...</Text>
            </Box>
          )}
          {summarizationDataStatus === 'not_found' && (
            <Box className="oai-appsum-not-found" bg="gray.900" p="20px" borderRadius="20px" width="60%" minWidth="600px">
              <Text>No summary data found.</Text>
            </Box>
          )}
        </VStack>
      </Center>
    </Box>
  );
};

export default ApplicantSummarization;
