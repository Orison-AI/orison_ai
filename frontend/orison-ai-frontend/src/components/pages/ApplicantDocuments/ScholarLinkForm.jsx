// ./components/pages/Documents/ScholarLinkForm.jsx

// React
import React, { useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import { doc, getDoc, setDoc } from 'firebase/firestore';

// Chakra
import {
  Button, FormControl, FormHelperText,
  HStack, Input, InputGroup, InputRightElement,
  Text, useToast,
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
// Will use TimeIcon when processing is in-progress

// Orison
import { processScholarLink } from '../../../api/api';

const ScholarLinkForm = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [scholarLink, setScholarLink] = useState('');
  const [scholarLinkSubmitted, setScholarLinkSubmitted] = useState(false);
  const toast = useToast();

  useEffect(() => {
    const fetchScholarLink = async () => {
      if (user && selectedApplicant) {
        const docRef = doc(db, "applicants", selectedApplicant.id);
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          setScholarLink(docSnap.data().scholarLink || '');
        }
      }
    };

    fetchScholarLink();
  }, [user, selectedApplicant]);

  const handleScholarSubmit = async (event) => {
    event.preventDefault();
    if (user && selectedApplicant) {
      try {
        await setDoc(doc(db, "applicants", selectedApplicant.id), {
          scholarLink,
        }, { merge: true });
        const response = await processScholarLink(user.uid, selectedApplicant.id, scholarLink);
        toast({
          title: 'Google Scholar Link Submitted',
          description: `Request ID: ${response.requestId}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        setScholarLinkSubmitted(true);
      } catch (error) {
        toast({
          title: 'Submission Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        setScholarLinkSubmitted(false);
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
              {scholarLinkSubmitted && (
                <CheckCircleIcon color="green.500" />
              )}
            </InputRightElement>
          </InputGroup>
          <Button type="submit" colorScheme="blue" ml="0.5vh">
            Submit
          </Button>
        </HStack>
      </form>
      <FormHelperText>Example: https://scholar.google.com/citations?user=XXXXX</FormHelperText>
    </FormControl>
  );
};

export default ScholarLinkForm;
