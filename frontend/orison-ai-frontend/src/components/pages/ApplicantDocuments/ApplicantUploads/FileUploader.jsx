// ./components/pages/ApplicantDocuments/ApplicantUploads/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../../common/firebaseConfig';
import {
  deleteObject, getDownloadURL, getMetadata, getStorage,
  listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Alert, AlertIcon, AlertDescription,
  Box, HStack, Icon, Link, Select,
  Text, useDisclosure, useToast, VStack,
} from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

// Orison
import { vectorizeFiles } from '../../../../api/api';
import DeleteFileModal from './DeleteFileModal';
import ViewFileModal from './ViewFileModal';
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
  const [fileToView, setFileToView] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const { isOpen: isViewModalOpen, onOpen: onViewModalOpen, onClose: onViewModalClose } = useDisclosure();
  const [isVectorizing, setIsVectorizing] = useState(false);

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

      // Determine the correct contentType
      let contentType = file.type;

      // Browser doesn't detect markdown files for some reason
      if (file.name.endsWith('.md')) {
        contentType = 'text/markdown';
      }

      const metadata = {
        contentType: contentType,
      };
  
      if (documents.includes(file.name)) {
        setFileToOverwrite(file);
        onOverwriteModalOpen();
      } else {
        try {
          await uploadBytes(storageRef, file, metadata);
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
      setIsVectorizing(true);  // Start vectorizing
      try {
        await vectorizeFiles(user.uid, selectedApplicant.id, [fileName]);
        toast({
          title: 'Vectorization Completed',
          description: `Vectorization for ${fileName} has completed successfully.`,
          status: 'success',
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
      } finally {
        setIsVectorizing(false);  // End vectorizing
      }
    }
  };

  const viewFile = async (fileName) => {
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${fileName}`;
    const storageRef = ref(getStorage(), filePath);
    
    try {
      // Get file metadata, which includes the content type
      const metadata = await getMetadata(storageRef);
      const contentType = metadata.contentType;

      // Determine if the file is text or binary based on contentType
      const textMimeTypes = [
        'text/plain', 'text/html', 'text/css', 'application/javascript', 'text/javascript',
        'application/json', 'application/xml', 'text/xml', 'text/markdown', 'text/csv',
        'application/x-yaml', 'text/yaml', 'text/x-vcard', 'text/x-vcalendar'
      ];
      
      const isTextFile = (mimeType) => textMimeTypes.includes(mimeType);
      let text = `Unable to display file of type: [${contentType}]`;

      if (isTextFile(contentType)) {
        const fileUrl = await getDownloadURL(storageRef);
        const response = await fetch(fileUrl);
        text = await response.text();
      }
      
      setFileToView(fileName);
      setFileContent(text);
      onViewModalOpen();

    } catch (error) {
      console.error(`Error fetching file content: ${error.message}`);
      toast({
        title: 'Error Fetching File Content',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <VStack width="100%" flex="1" mt="20px" overflowY="auto" overflowX="auto">
      <HStack width="100%" fontSize="24px">
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
      <Alert status="warning" minHeight="80px" borderRadius="10px" mb="4" fontSize="16px">
        <AlertIcon />
        <AlertDescription>
        Only vectorized files are included in the applicant summary generated by the AI model, and currently only one file may be vectorized at a time.
          Vectorizing a file will delete the vectors for any other file.
          Support for multiple files will be added in a future version.
        </AlertDescription>
      </Alert>
      <VStack
        {...getRootProps()}
        border="2px dashed gray"
        w="100%"
        p="20px"
        mb="20px"
        backgroundColor={isDragActive ? 'gray.700' : 'transparent'}
      >
        <input {...getInputProps()} />
        <Icon as={DownloadIcon} color="gray.500" />
        <Text fontSize="20px">
          <Link as="b" onClick={open} cursor="pointer">Choose a file</Link> or drag it here
        </Text>
      </VStack>
      <FileTable
        documents={documents}
        processedFiles={processedFiles}
        vectorizeFile={vectorizeFile}
        deleteFile={deleteFile}
        viewFile={viewFile}
        isVectorizing={isVectorizing}
      />
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
      <ViewFileModal
        isOpen={isViewModalOpen}
        onClose={onViewModalClose}
        fileName={fileToView}
        fileContent={fileContent}
      />
    </VStack>
  );
};

export default FileUploader;
