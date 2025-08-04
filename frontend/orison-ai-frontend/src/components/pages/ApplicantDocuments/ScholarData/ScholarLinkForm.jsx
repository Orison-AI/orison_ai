// ./components/pages/ApplicantDocuments/ScholarData/ScholarLinkForm.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../../common/firebaseConfig';
import {
  collection, doc, getDoc, getDocs,
  limit, orderBy, query, setDoc,
} from 'firebase/firestore';

// Chakra UI
import {
  Alert, AlertDescription, AlertIcon, AlertTitle,
  Box, Button, FormControl, FormHelperText, FormLabel,
  HStack, Input, InputGroup, InputRightElement,
  Spinner, Text, useDisclosure, useToast,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';

// Orison AI
import { processScholarLink } from '../../../../api/api';
import { processScholarNetwork } from '../../../../api/api';
import ScholarDataModal from './ScholarDataModal';
import { useApplicantContext } from '../../../../context/ApplicantContext';

const ScholarLinkForm = ({ }) => {
  const [user] = useAuthState(auth);
  const [scholarLink, setScholarLink] = useState('');
  const [scholarDataStatus, setScholarDataStatus] = useState('');
  const [scholarData, setScholarData] = useState(null);
  const [maxDepth, setMaxDepth] = useState('3');
  const [maxEntries, setMaxEntries] = useState('20');
  const { isOpen: isScholarDataModalOpen, onOpen: onScholarDataModalOpen, onClose: onScholarDataModalClose } = useDisclosure();
  const toast = useToast();
  const { selectedApplicant } = useApplicantContext();

  const fetchScholarData = useCallback(async () => {
    if (user && selectedApplicant) {
      setScholarDataStatus('loading');
      try {
        const scholarQuery = query(
          collection(doc(collection(db, "google_scholar"), user.uid), selectedApplicant.id),
          orderBy("date_created", "desc"),
          limit(1)
        );
        const scholarNetworkQuery = query(
          collection(doc(collection(db, "google_scholar_network"), user.uid), selectedApplicant.id),
          orderBy("date_created", "desc"),
          limit(1)
        );
        
        const [querySnapshot, networkSnapshot] = await Promise.all([
          getDocs(scholarQuery),
          getDocs(scholarNetworkQuery)
        ]);
        
        if (querySnapshot.empty) {
          setScholarData(null);
          setScholarDataStatus('not_found');
          return;
        }
        
        const scholarData = querySnapshot.docs[0].data();
        const networkData = networkSnapshot.empty ? null : networkSnapshot.docs[0].data();
        
        // Merge data with proper fallbacks
        const mergedData = {
          ...scholarData,
          network: networkData?.network || [],
        };
        
        setScholarData(mergedData);
        setScholarDataStatus('found');
      } catch (error) {
        console.error('Error fetching scholar data:', error);
        setScholarData(null);
        setScholarDataStatus('not_found');
      }
    }
  }, [user, selectedApplicant]);

  useEffect(() => {
    const fetchScholarLink = async () => {
      if (selectedApplicant) {
        // Check applicants collection for scholar link and settings
        const docRef = doc(db, "applicants", selectedApplicant.id);
        // Get the scholar link from the database
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          const data = docSnap.data();
          // Use scholar link from the database
          setScholarLink(data.scholarLink || '');
                      // Load saved settings if they exist
            if (data.scholarMaxDepth) setMaxDepth(String(data.scholarMaxDepth));
            if (data.scholarMaxEntries) setMaxEntries(String(data.scholarMaxEntries));
        }
      }
    };

    fetchScholarLink();
    fetchScholarData();
  }, [fetchScholarData, selectedApplicant]);

  const handleScholarSearchRequest = async (event) => {
    event.preventDefault();
    if (user && selectedApplicant) {
      try {
        // Save scholar link and settings first
        await setDoc(doc(db, "applicants", selectedApplicant.id), {
          scholarLink,
          scholarMaxDepth: parseInt(maxDepth) || 3,
          scholarMaxEntries: parseInt(maxEntries) || 20,
        }, { merge: true });

        // Show initial toast
        const depth = parseInt(maxDepth) || 3;
        const entries = parseInt(maxEntries) || 20;
        const estimatedTime = Math.ceil(depth * entries / 10) * 2;
        toast({
          title: 'Starting Google Scholar Data Processing',
          description: `Processing scholar profile and network (depth: ${depth}, max: ${entries}) with 0.25-second gap. This may take ${estimatedTime}-${estimatedTime * 2} minutes.`,
          status: 'info',
          duration: 10000,
          isClosable: true,
        });

        setScholarDataStatus('loading');

        // Start both operations with a small delay between them
        // First process the scholar link immediately
        processScholarLink(user.uid, selectedApplicant.id, scholarLink)
          .then(() => {
            console.log('Scholar link processing started');
          })
          .catch(error => {
            console.error('Scholar link processing error:', error);
          });

        // Then process the network after a 0.25-second delay
        setTimeout(() => {
          console.log('Starting network processing...');
          processScholarNetwork(user.uid, selectedApplicant.id, scholarLink, parseInt(maxDepth) || 3, parseInt(maxEntries) || 20)
            .then(() => {
              console.log('Network processing started');
            })
            .catch(error => {
              console.error('Network processing error:', error);
            });
        }, 250);

        // Track completion status
        let scholarCompleted = false;
        let networkCompleted = false;
        
        // Start polling for results
        const pollInterval = setInterval(async () => {
          try {
            await fetchScholarData();
            
            // Check if we have scholar data
            if (scholarData && Object.keys(scholarData).length > 0 && !scholarCompleted) {
              scholarCompleted = true;
              toast({
                title: 'Scholar Profile Complete!',
                description: 'Scholar profile data has been processed and is available.',
                status: 'success',
                duration: 5000,
                isClosable: true,
              });
            }
            
            // Check if we have network data
            if (scholarData && scholarData.network && scholarData.network.length > 0 && !networkCompleted) {
              networkCompleted = true;
              toast({
                title: 'Network Analysis Complete!',
                description: 'Co-author network data has been processed and is available.',
                status: 'success',
                duration: 5000,
                isClosable: true,
              });
            }
            
            // If both are complete, stop polling
            if (scholarCompleted && networkCompleted) {
              clearInterval(pollInterval);
              setScholarDataStatus('found');
            }
          } catch (error) {
            console.error('Polling error:', error);
          }
        }, 30000); // Check every 30 seconds

        // Stop polling after 60 minutes (120 checks)
        setTimeout(() => {
          clearInterval(pollInterval);
          if (scholarDataStatus === 'loading') {
            setScholarDataStatus('not_found');
            toast({
              title: 'Processing Timeout',
              description: 'Google Scholar processing is taking longer than expected. Please check back later.',
              status: 'warning',
              duration: 10000,
              isClosable: true,
            });
          }
        }, 60 * 60 * 1000); // 60 minutes

      } catch (error) {
        setScholarDataStatus('not_found');
        toast({
          title: 'Google Scholar Search Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  return (
    <Box width="100%">
      <FormControl>
        <Text width="100%" mb="8px" fontSize="24px">Google Scholar</Text>
        <form onSubmit={handleScholarSearchRequest}>
          <HStack>
            <InputGroup>
              <Input
                placeholder="Enter Google Scholar URL"
                value={scholarLink}
                onChange={(e) => setScholarLink(e.target.value)}
                isDisabled={scholarDataStatus === 'loading'}
              />
              <InputRightElement>
                {(scholarDataStatus === 'loading') && (
                  <Spinner color="blue.500" size="sm" />
                )}
                {(scholarDataStatus === 'found') && (
                  <CheckCircleIcon color="green.500" />
                )}
                {(scholarDataStatus === 'not_found') && (
                  <WarningIcon color="red.500" />
                )}
              </InputRightElement>
            </InputGroup>
            <Button
              type="submit"
              colorScheme="blue"
              ml="4px"
              isDisabled={scholarDataStatus === 'loading'}
            >
              Search
            </Button>
            <Button onClick={onScholarDataModalOpen} ml="4px" isDisabled={scholarDataStatus !== 'found'}>
              View
            </Button>
            <Button 
              onClick={fetchScholarData} 
              ml="4px" 
              variant="outline"
              isLoading={scholarDataStatus === 'loading'}
            >
              Refresh
            </Button>
          </HStack>
        </form>
        <FormHelperText>Example: https://scholar.google.com/citations?user=XXXXX</FormHelperText>
        
        {/* Simple Network Configuration */}
        <HStack mt={4} spacing={4}>
          <FormControl>
            <FormLabel fontSize="sm">Max Depth</FormLabel>
            <Input
              type="number"
              value={maxDepth}
              onChange={(e) => setMaxDepth(e.target.value)}
              min={1}
              max={5}
              size="sm"
              width="100px"
            />
            <FormHelperText fontSize="xs">Levels to explore (1-5)</FormHelperText>
          </FormControl>

          <FormControl>
            <FormLabel fontSize="sm">Max Entries</FormLabel>
            <Input
              type="number"
              value={maxEntries}
              onChange={(e) => setMaxEntries(e.target.value)}
              min={5}
              max={100}
              size="sm"
              width="100px"
            />
            <FormHelperText fontSize="xs">Max scholars (5-100)</FormHelperText>
          </FormControl>
        </HStack>
        {scholarDataStatus === 'loading' && (
          <Alert status="info" mt={2}>
            <AlertIcon />
            <Box>
              <AlertTitle>Processing Google Scholar Data</AlertTitle>
              <AlertDescription>
                Processing scholar profile and network (depth: {parseInt(maxDepth) || 3}, max: {parseInt(maxEntries) || 20}) with 0.25-second gap<br/>
                Estimated time: {Math.ceil((parseInt(maxDepth) || 3) * (parseInt(maxEntries) || 20) / 10) * 2}-{Math.ceil((parseInt(maxDepth) || 3) * (parseInt(maxEntries) || 20) / 10) * 4} minutes<br/>
                Both operations start independently with 0.25-second gap. You can close this window and check back later using the Refresh button.
              </AlertDescription>
            </Box>
          </Alert>
        )}
      </FormControl>
      <ScholarDataModal isOpen={isScholarDataModalOpen} onClose={onScholarDataModalClose} data={scholarData} />
    </Box>
  );
};

export default ScholarLinkForm;
