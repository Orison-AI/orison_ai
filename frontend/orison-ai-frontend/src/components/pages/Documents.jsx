// ./components/pages/Documents.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import {
  deleteObject, getStorage, listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Box, Button, HStack, IconButton, Input,
  FormControl, FormLabel, FormHelperText,
  Table, Thead, Tbody, Tr, Th, Td,
  Text, useToast, VStack, Badge,
  InputGroup, InputRightElement,
} from '@chakra-ui/react';
import { CloseIcon, CheckCircleIcon } from '@chakra-ui/icons';
// Will use TimeIcon for in-progress processing

// Dropzone
import { useDropzone } from 'react-dropzone';

// Internal
import { auth } from '../../firebaseConfig';
import { processScholarLink } from '../../api/api';

const ApplicantDocuments = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const toast = useToast();
  const [documents, setDocuments] = useState([]);
  const [scholarLink, setScholarLink] = useState('');
  const [processedFiles, setProcessedFiles] = useState([]);
  const [scholarLinkSubmitted, setScholarLinkSubmitted] = useState(false);

  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/`;
      const storage = getStorage();
      const listRef = ref(storage, filePath);
      
      try {
        const res = await listAll(listRef);
        const docs = res.items.map(itemRef => (itemRef.name));
        setDocuments(docs);
      } catch (error) {
        console.error("Error fetching documents:", error);
      }
    }
  }, [user, selectedApplicant]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = async (acceptedFiles) => {
    const storage = getStorage();
  
    acceptedFiles.forEach(async (file) => {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${file.name}`;
      const storageRef = ref(storage, filePath);
  
      try {
        // Upload the file to Firebase Storage
        await uploadBytes(storageRef, file);

        // Fetch updated documents
        fetchDocuments();
      } catch (error) {
        console.error(`Error uploading file: ${error.message}`);
        toast({
          title: 'Error Uploading File',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }
    });
  };

  const deleteFile = async (fileName) => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${fileName}`;
    const storageRef = ref(storage, filePath);
  
    try {
      // Delete the file from Firebase Storage
      await deleteObject(storageRef);
  
      toast({
        title: 'File Deleted',
        description: `File ${fileName} deleted successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
  
      // Fetch updated documents
      fetchDocuments();
    } catch (error) {
      console.error(`Error deleting file: ${error.message}`);
      toast({
        title: 'Error Deleting File',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleScholarSubmit = async (event) => {
    event.preventDefault(); // Prevent the default form submission behavior
    if (user && selectedApplicant) {
      try {
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

  const vectorizeFile = async (fileName) => {
    // Implement the vectorize file function
    setProcessedFiles(prevState => [...prevState, fileName]);
    toast({
      title: 'Vectorization Started',
      description: `Vectorization for ${fileName} has started.`,
      status: 'info',
      duration: 5000,
      isClosable: true,
    });
  };

  const vectorizeAllFiles = async () => {
    // Implement the vectorize all files function
    setProcessedFiles(documents);  // Assuming all documents will be processed
    toast({
      title: 'Vectorization Started',
      description: 'Vectorization for all files has started.',
      status: 'info',
      duration: 5000,
      isClosable: true,
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <VStack height="100%" width="100%" padding="2vh" fontSize="4vh">
      <HStack width="100%">
        <Text fontSize="3vh" ml="2vh" mb="4vh" color="gray.400">Documents &gt;</Text>
        <Text fontSize="3vh" mb="4vh" color="green.300" as="strong">
          {selectedApplicant ? selectedApplicant.name : "None"}
        </Text>
      </HStack>
      <FormControl width="50%">
        <FormLabel>Google Scholar Link</FormLabel>
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
      <VStack {...getRootProps()} border="2px dashed gray" padding="20px" width="50%" marginTop="4vh">
        <input {...getInputProps()} />
        {
          isDragActive ?
            <Text>Drop the files here...</Text> :
            <Text>Drag files here or click to select files</Text>
        }
      </VStack>
      <Box mt="4vh" mb="2vh" width="50%" overflowY="auto" overflowX="auto" border="1px" borderColor="gray.600" borderRadius="1vh">
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>File Name</Th>
              <Th>Status</Th>
              <Th></Th>
            </Tr>
          </Thead>
          <Tbody fontSize="2vh">
            {documents.map(fileName => (
              <Tr key={fileName}>
                <Td>
                  {fileName} 
                  {(processedFiles.includes(fileName)) && (
                    <CheckCircleIcon ml="2" color="green.500" />
                  )}
                </Td>
                <Td>
                  {processedFiles.includes(fileName) ? (
                    <Badge colorScheme="green">Vectorized</Badge>
                  ) : (
                    <Badge colorScheme="yellow">Not Vectorized</Badge>
                  )}
                </Td>
                <Td isNumeric>
                  <Button ml="2vh" mr="2vh" colorScheme="blue" onClick={() => vectorizeFile(fileName)}>
                    Vectorize
                  </Button>
                  <IconButton
                    icon={<CloseIcon />}
                    colorScheme="red"
                    variant="ghost"
                    onClick={() => deleteFile(fileName)}
                  />
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
      <Button mb="4vh" colorScheme="blue" onClick={vectorizeAllFiles}>
        Vectorize All
      </Button>
    </VStack>
  );
}

export default ApplicantDocuments;
