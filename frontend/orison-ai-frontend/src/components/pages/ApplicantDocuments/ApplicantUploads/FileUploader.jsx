// ./components/pages/ApplicantDocuments/ApplicantUploads/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../../common/firebaseConfig';
import {
  deleteObject, getStorage, listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Box, HStack, Icon, Link, Select,
  Text, useDisclosure, useToast, VStack,
} from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

// Orison
import { vectorizeFiles } from '../../../../api/api';
import DeleteFileModal from './DeleteFileModal';
import FileTable from './FileTable';
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

  return (
    <VStack width="50%" height="50vh" mt="4vh">
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
      <FileTable
        documents={documents}
        processedFiles={processedFiles}
        vectorizeFile={vectorizeFile}
        deleteFile={deleteFile}
      />
      <VStack
        {...getRootProps()}
        border="2px dashed gray"
        p="2vh"
        mb="2vh"
        backgroundColor={isDragActive ? 'gray.700' : 'transparent'}
      >
        <input {...getInputProps()} />
        <Icon as={DownloadIcon} w="4vh" h="4vh" mt="2vh" mb="2vh" color="gray.500" />
        <Text fontSize="20px">
          <Link as="b" onClick={open} cursor="pointer">Choose a file</Link> or drag it here
        </Text>
      </VStack>
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
