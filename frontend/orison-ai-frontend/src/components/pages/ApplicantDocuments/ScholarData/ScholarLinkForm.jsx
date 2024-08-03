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
  Box, Button, FormControl, FormHelperText,
  HStack, Input, InputGroup, InputRightElement,
  Spinner, Text, useDisclosure, useToast,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';

// Orison AI
import { processScholarLink } from '../../../../api/api';
import { processScholarNetwork } from '../../../../api/api';
import ScholarDataModal from './ScholarDataModal';

const ScholarLinkForm = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [scholarLink, setScholarLink] = useState('');
  const [scholarDataStatus, setScholarDataStatus] = useState('');
  const [scholarData, setScholarData] = useState(null);
  const { isOpen: isScholarDataModalOpen, onOpen: onScholarDataModalOpen, onClose: onScholarDataModalClose } = useDisclosure();
  const toast = useToast();

  const fetchScholarData = useCallback(async () => {
    if (user && selectedApplicant) {
      setScholarDataStatus('loading');
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
      const querySnapshot = await getDocs(scholarQuery);
      const networkSnapshot = await getDocs(scholarNetworkQuery);
      if (querySnapshot.empty || networkSnapshot.empty) {
        setScholarData(null);
        setScholarDataStatus('not_found');
      } else {
        const data = querySnapshot.docs[0].data();
        const networkData = networkSnapshot.docs[0].data();
        const mergedData = {...data, ...networkData};
        setScholarData(mergedData);
        setScholarDataStatus('found');
      }
    }
  }, [user, selectedApplicant]);

  useEffect(() => {
    const fetchScholarLink = async () => {
      if (selectedApplicant) {
        // Check applicants collection for scholar link
        const docRef = doc(db, "applicants", selectedApplicant.id);
        // Get the scholar link from the database
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          // Use scholar link from the database
          setScholarLink(docSnap.data().scholarLink || '');
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
        toast({
          title: 'Searching for Google Scholar Data',
          description: 'Please wait for processing',
          status: 'loading',
          duration: 5000,
          isClosable: true,
        });
        setScholarDataStatus('loading');
        await Promise.all([
          processScholarLink(user.uid, selectedApplicant.id, scholarLink),
          processScholarNetwork(user.uid, selectedApplicant.id, scholarLink)
        ]);
        
        toast({
          title: 'Google Scholar Data Found',
          description: `Link: ${scholarLink}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        await setDoc(doc(db, "applicants", selectedApplicant.id), {
          scholarLink,
        }, { merge: true });
        await fetchScholarData();
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
          </HStack>
        </form>
        <FormHelperText>Example: https://scholar.google.com/citations?user=XXXXX</FormHelperText>
      </FormControl>
      <ScholarDataModal isOpen={isScholarDataModalOpen} onClose={onScholarDataModalClose} data={scholarData} />
    </Box>
  );
};

export default ScholarLinkForm;
