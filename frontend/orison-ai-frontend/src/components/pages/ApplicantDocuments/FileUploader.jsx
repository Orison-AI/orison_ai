// ./components/pages/ApplicantDocuments/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../common/firebaseConfig';
import {
  deleteObject, getStorage, listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Badge, Box, Button, HStack, Icon, IconButton, Link, Select,
  Table, Thead, Tbody, Tr, Th, Td,
  Text, useDisclosure, useToast, VStack,
} from '@chakra-ui/react';
import { CloseIcon, CheckCircleIcon, DownloadIcon } from '@chakra-ui/icons';
// Will use TimeIcon when processing is in-progress

// Orison
import { vectorizeFiles } from '../../../api/api';
import DeleteFileModal from './DeleteFileModal';
import OverwriteFileModal from './OverwriteFileModal';

const buckets = ["research", "reviews", "awards", "feedback"];

const FileUploader = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [documents, setDocuments] = useState([]);
  const [processedFiles, setProcessedFiles] = useState([]);
  const [selectedBucket, setSelectedBucket] = useState(buckets[0]);
  const [fileToOverwrite, setFileToOverwrite] = useState(null);
  const { isOpen: isOverwriteModalOpen, onOpen: onOverwriteModalOpen, onClose: onOverwriteModalClose } = useDisclosure();
  const [fileToDelete, setFileToDelete] = useState(null);
  const { isOpen: isDeleteModalOpen, onOpen: onDeleteModalOpen, onClose: onDeleteModalClose } = useDisclosure();
  const toast = useToast();

  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/`;
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
  }, [user, selectedApplicant, selectedBucket]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments, selectedBucket]);

  const onDrop = async (acceptedFiles) => {
    const storage = getStorage();
  
    for (const file of acceptedFiles) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${file.name}`;
      const storageRef = ref(storage, filePath);
  
      if (documents.includes(file.name)) {
        setFileToOverwrite(file);
        onOverwriteModalOpen();
      } else {
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
        }
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({ onDrop });

  const handleOverwriteConfirm = async () => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${fileToOverwrite.name}`;
    const storageRef = ref(storage, filePath);
  
    try {
      await uploadBytes(storageRef, fileToOverwrite);
      setProcessedFiles(prevState => prevState.filter(fileName => fileName !== fileToOverwrite.name));
      fetchDocuments();
      onOverwriteModalClose();
      setFileToOverwrite(null);
    } catch (error) {
      console.error(`Error uploading file: ${error.message}`);
      toast({
        title: 'Error Uploading File',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const deleteFile = (fileName) => {
    setFileToDelete(fileName);
    onDeleteModalOpen();
  };
  
  const handleDeleteConfirm = async () => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${fileToDelete}`;
    const storageRef = ref(storage, filePath);
  
    try {
      await deleteObject(storageRef);
      toast({
        title: 'File Deleted',
        description: `File ${fileToDelete} deleted successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      fetchDocuments();
      onDeleteModalClose();
      setFileToDelete(null);
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

  const vectorizeFile = async (bucketName, fileName) => {
    if (user && selectedApplicant) {
      try {
        const tag = bucketName;
        const response = await vectorizeFiles(user.uid, selectedApplicant.id, bucketName, tag, [fileName]);
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

  return (
    <VStack width="50%" mt="4vh">
      <HStack width="100%" mb="0.5vh" fontSize="24px">
        <Text width="100%">Applicant Files</Text>
        <Box minWidth="200px" fontSize="24px">
          <Select value={selectedBucket} onChange={(e) => setSelectedBucket(e.target.value)} color="blue.100">
            {buckets.map((bucket) => (
              <option key={bucket} value={bucket}>
                {bucket.charAt(0).toUpperCase() + bucket.slice(1)}
              </option>
            ))}
          </Select>
        </Box>
      </HStack>
      <Box mb="20px" width="100%" overflowY="auto" overflowX="auto" border="1px" borderColor="gray.600" borderRadius="1vh">
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>File Name</Th>
              <Th>Status</Th>
              <Th></Th>
            </Tr>
          </Thead>
          <Tbody fontSize="20px">
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
                  <Button ml="2vh" mr="2vh" colorScheme="blue" onClick={() => vectorizeFile(selectedBucket, fileName)}>
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
        <VStack
          {...getRootProps()}
          border="2px dashed gray"
          p="2vh"
          m="2vh"
          backgroundColor={isDragActive ? 'gray.700' : 'transparent'}
        >
          <input {...getInputProps()} />
          <Icon as={DownloadIcon} w="4vh" h="4vh" mt="2vh" mb="2vh" color="gray.500" />
          <Text fontSize="20px">
            <Link as="b" onClick={open} cursor="pointer">Choose a file</Link> or drag it here
          </Text>
        </VStack>
      </Box>
      <OverwriteFileModal
        isOpen={isOverwriteModalOpen}
        onClose={onOverwriteModalClose}
        onConfirm={handleOverwriteConfirm}
        fileName={fileToOverwrite?.name}
      />
      <DeleteFileModal
        isOpen={isDeleteModalOpen}
        onClose={onDeleteModalClose}
        onConfirm={handleDeleteConfirm}
        fileName={fileToDelete}
      />
    </VStack>
  );
};

export default FileUploader;
