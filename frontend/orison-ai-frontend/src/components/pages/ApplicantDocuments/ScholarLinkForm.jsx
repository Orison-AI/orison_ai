// ./components/pages/Documents/ScholarLinkForm.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import {
  collection, doc, getDoc, getDocs,
  limit, orderBy, query, setDoc, where,
} from 'firebase/firestore';


// Chakra
import {
  Button, FormControl, FormHelperText,
  HStack, Input, InputGroup, InputRightElement,
  Text, useToast,
} from '@chakra-ui/react';
import { CheckCircleIcon, TimeIcon, WarningIcon } from '@chakra-ui/icons';

// Orison
import { processScholarLink } from '../../../api/api';

const ScholarLinkForm = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [scholarLink, setScholarLink] = useState('');
  const [scholarDataStatus, setScholarDataStatus] = useState('');
  const toast = useToast();

  const fetchScholarData = useCallback(async () => {
    if (user && selectedApplicant) {
      // Check google_scholar collection for latest data

      // Update status icons for loading
      setScholarDataStatus('loading');
  
      // Create the query
      const scholarQuery = query(
        collection(db, "google_scholar"),
        where("attorney_id", "==", user.uid),
        where("applicant_id", "==", selectedApplicant.id),
        orderBy("date_created", "desc"),
        limit(1)
      );

      // Perform the query
      const querySnapshot = await getDocs(scholarQuery);

      // Update status icons based on result of query
      if (querySnapshot.empty) {
        setScholarDataStatus('not_found');
      } else {
        setScholarDataStatus('found');
      }
    }
  }, [user, selectedApplicant, setScholarDataStatus]);

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

  const handleScholarSubmit = async (event) => {
    event.preventDefault();
    if (user && selectedApplicant) {
      try {
        await setDoc(doc(db, "applicants", selectedApplicant.id), {
          scholarLink,
        }, { merge: true });
        toast({
          title: 'Searching for Google Scholar Data',
          description: 'Please wait for processing',
          status: 'loading',
          duration: 5000,
          isClosable: true,
        });
        setScholarDataStatus('loading');
        await processScholarLink(user.uid, selectedApplicant.id, scholarLink);
        toast({
          title: 'Google Scholar Data Found',
          description: `Link: ${scholarLink}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        await fetchScholarData();
      } catch (error) {
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
    <FormControl width="50%">
      <Text width="100%" mb="1vh" fontSize="24px">Google Scholar</Text>
      <form onSubmit={handleScholarSubmit}>
        <HStack>
          <InputGroup>
            <Input 
              placeholder="Enter Google Scholar URL" 
              value={scholarLink}
              onChange={(e) => setScholarLink(e.target.value)}
            />
            <InputRightElement>
              {(scholarDataStatus === 'loading') && (
                <TimeIcon color="blue.500" />
              )}
              {(scholarDataStatus === 'found') && (
                <CheckCircleIcon color="green.500" />
              )}
              {(scholarDataStatus === 'not_found') && (
                <WarningIcon color="red.500" />
              )}
            </InputRightElement>
          </InputGroup>
          <Button type="submit" colorScheme="blue" ml="0.5vh">
            Search
          </Button>
        </HStack>
      </form>
      <FormHelperText>Example: https://scholar.google.com/citations?user=XXXXX</FormHelperText>
    </FormControl>
  );
};

export default ScholarLinkForm;
