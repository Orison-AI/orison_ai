// ./components/pages/Documents/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../firebaseConfig';
import {
  deleteObject, getStorage, listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Box, Button, FormLabel, IconButton,
  Table, Thead, Tbody, Tr, Th, Td,
  Text, VStack, Badge, useToast,
} from '@chakra-ui/react';
import { CloseIcon, CheckCircleIcon } from '@chakra-ui/icons';

// Orison
import { vectorizeFiles } from '../../../api/api';

const FileUploader = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [documents, setDocuments] = useState([]);
  const [processedFiles, setProcessedFiles] = useState([]);
  const toast = useToast();

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
        await uploadBytes(storageRef, file);
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

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const deleteFile = async (fileName) => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${fileName}`;
    const storageRef = ref(storage, filePath);
  
    try {
      await deleteObject(storageRef);
      toast({
        title: 'File Deleted',
        description: `File ${fileName} deleted successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
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

  const vectorizeFile = async (fileName) => {
    if (user && selectedApplicant) {
      try {
        const response = await vectorizeFiles(user.uid, selectedApplicant.id, [fileName]);
        toast({
          title: 'Vectorization Started',
          description: `Vectorization for ${fileName} has started. Request ID: ${response.requestId}`,
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
        setProcessedFiles(prevState => [...prevState, fileName]);
      } catch (error) {
        toast({
          title: 'Vectorization Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const vectorizeAllFiles = async () => {
    if (user && selectedApplicant) {
      try {
        const response = await vectorizeFiles(user.uid, selectedApplicant.id, documents);
        toast({
          title: 'Vectorization Started',
          description: `Vectorization for all files has started. Request ID: ${response.requestId}`,
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
        setProcessedFiles(documents);
      } catch (error) {
        toast({
          title: 'Vectorization Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  return (
    <>
      <FormLabel width="50%" mt="4vh" mb="2vh">Applicant Files</FormLabel>
      <Box mb="2vh" width="50%" overflowY="auto" overflowX="auto" border="1px" borderColor="gray.600" borderRadius="1vh">
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
                    <Badge colorScheme="orange">Not Vectorized</Badge>
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
        <VStack {...getRootProps()} border="2px dashed gray" padding="20px" width="100%">
          <input {...getInputProps()} />
          {
            isDragActive ?
              <Text>Drop the files here...</Text> :
              <Text>Drag files here or click to select files</Text>
          }
        </VStack>
      </Box>
      <Button mb="4vh" colorScheme="blue" onClick={vectorizeAllFiles}>
        Vectorize All
      </Button>
    </>
  );
};

export default FileUploader;
