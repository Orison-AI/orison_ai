// ./components/pages/ApplicantDocuments/ApplicantUploads/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../../common/firebaseConfig';
import { doc, getDoc } from 'firebase/firestore';
import {
  deleteObject, getDownloadURL, getMetadata, getStorage,
  listAll, ref, uploadBytes,
} from 'firebase/storage';

// Chakra
import {
  Alert, AlertIcon, AlertDescription,
  Box, HStack, Select, Text,
  useDisclosure, useToast, VStack, Button,
} from '@chakra-ui/react';

// Orison
import { vectorizeFiles, deleteFileVectors } from '../../../../api/api';
import FileDropzone from './FileDropzone';
import FileTable from './FileTable';
import OverwriteFileModal from './OverwriteFileModal';
import UploadingFileModal from './UploadingFileModal';
import ViewFileModal from './ViewFileModal';
import DeleteFileModal from './DeleteFileModal';
import DeletingFileModal from './DeletingFileModal';


const buckets = ["research", "reviews", "awards", "feedback"];

const FileUploader = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [documents, setDocuments] = useState([]);
  const [selectedBucket, setSelectedBucket] = useState(buckets[0]);
  const [fileToOverwrite, setFileToOverwrite] = useState(null);
  const {
    isOpen: isOverwriteModalOpen,
    onOpen: onOverwriteModalOpen,
    onClose: onOverwriteModalClose,
  } = useDisclosure();
  const [fileToDelete, setFileToDelete] = useState(null);
  const {
    isOpen: isDeleteModalOpen,
    onOpen: onDeleteModalOpen,
    onClose: onDeleteModalClose,
  } = useDisclosure();
  const [fileToView, setFileToView] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const {
    isOpen: isViewModalOpen,
    onOpen: onViewModalOpen,
    onClose: onViewModalClose,
  } = useDisclosure();
  const [vectorizingFiles, setVectorizingFiles] = useState([]);  // Array to track multiple vectorizations
  const [vectorizeStatus, setVectorizeStatus] = useState('');
  const [vectorizedFiles, setVectorizedFiles] = useState([]);
  const [uploadInProgress, setUploadInProgress] = useState(false);
  const [uploadingFileName, setUploadingFileName] = useState('');
  const {
    isOpen: isUploadModalOpen,
    onOpen: onUploadModalOpen,
    onClose: onUploadModalClose,
  } = useDisclosure();
  const [deletingFileName, setDeletingFileName] = useState('');
  const {
    isOpen: isDeleteInProgressModalOpen,
    onOpen: onDeleteInProgressModalOpen,
    onClose: onDeleteInProgressModalClose,
  } = useDisclosure();
  const toast = useToast();

  const fetchVectorizedFiles = useCallback(async () => {
    if (user && selectedApplicant) {
      const docRef = doc(db, "applicants", selectedApplicant.id);
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        setVectorizedFiles(docSnap.data().vectorized_files || []);
      }
    }
  }, [user, selectedApplicant]);

  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/`;
      const storage = getStorage();
      const listRef = ref(storage, filePath);

      try {
        const res = await listAll(listRef);
        const docs = res.items.map(itemRef => ({
          fileName: itemRef.name,
          vectorized: vectorizedFiles.includes(itemRef.name),
        }));
        setDocuments(docs);
      } catch (error) {
        console.error("Error fetching documents:", error);
      }
    }
  }, [user, selectedApplicant, selectedBucket, vectorizedFiles]);

  useEffect(() => {
    fetchVectorizedFiles();
  }, [fetchVectorizedFiles]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments, selectedBucket]);

  useEffect(() => {
    if (vectorizeStatus === 'success') {
      fetchVectorizedFiles();
    }
  }, [vectorizeStatus, fetchVectorizedFiles]);

  const onDrop = async (acceptedFiles) => {
    const storage = getStorage();

    for (const file of acceptedFiles) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${file.name}`;
      const storageRef = ref(storage, filePath);

      let contentType = file.type;
      if (file.name.endsWith('.md')) {
        contentType = 'text/markdown';
      }

      const metadata = {
        contentType: contentType,
      };

      if (documents.some(doc => doc.fileName === file.name)) {
        setFileToOverwrite(file);
        onOverwriteModalOpen();
      } else {
        try {
          setUploadingFileName(file.name);
          setUploadInProgress(true);
          onUploadModalOpen();
          await uploadBytes(storageRef, file, metadata);
          fetchDocuments();
          setUploadInProgress(false);
          onUploadModalClose();
        } catch (error) {
          console.error(`Error uploading file: ${error.message}`);
          toast({
            title: 'Error Uploading File',
            description: error.message,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          setUploadInProgress(false);
          onUploadModalClose();
        }
      }
    }
  };

  const handleOverwriteConfirm = async () => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${fileToOverwrite.name}`;
    const storageRef = ref(storage, filePath);

    try {
      await uploadBytes(storageRef, fileToOverwrite);
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
      setDeletingFileName(fileToDelete);
      onDeleteInProgressModalOpen();

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

      await deleteFileVectors(user.uid, selectedApplicant.id, selectedBucket, fileToDelete);
      setFileToDelete(null);
      onDeleteInProgressModalClose();
    } catch (error) {
      console.error(`Error deleting file: ${error.message}`);
      toast({
        title: 'Error Deleting File',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      onDeleteInProgressModalClose();
    }
  };

  const vectorizeFile = useCallback(async (fileName) => {
    if (user && selectedApplicant) {
      setVectorizingFiles((prev) => [...prev, fileName]);
      setVectorizeStatus('loading');
      try {
        await vectorizeFiles(user.uid, selectedApplicant.id, selectedBucket, fileName);
        toast({
          title: 'Vectorization Completed',
          description: `Vectorization for ${fileName} has completed successfully.`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        setVectorizeStatus('success');
      } catch (error) {
        toast({
          title: 'Vectorization Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        setVectorizeStatus('error');
      } finally {
        setVectorizingFiles((prev) => prev.filter((file) => file !== fileName));
      }
    }
  }, [selectedApplicant, selectedBucket, toast, user]);

  const vectorizeAllFiles = useCallback(async () => {
    const nonVectorizedFiles = documents.filter(doc => !doc.vectorized).map(doc => doc.fileName);
    for (const fileName of nonVectorizedFiles) {
      await vectorizeFile(fileName);
    }
  }, [documents, vectorizeFile]);

  const unvectorizeFile = (fileName) => {
    toast({
      title: 'Unvectorize Not Implemented',
      description: `Unvectorizing ${fileName} is not yet implemented.`,
      status: 'warning',
      duration: 3000,
      isClosable: true,
    });
  };

  const unvectorizeAllFiles = () => {
    toast({
      title: 'Unvectorize Not Implemented',
      description: 'Unvectorizing all files is not yet implemented.',
      status: 'warning',
      duration: 3000,
      isClosable: true,
    });
  };

  const viewFile = useCallback(async (fileName) => {
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedBucket}/${fileName}`;
    const storageRef = ref(getStorage(), filePath);

    try {
      const metadata = await getMetadata(storageRef);
      const contentType = metadata.contentType;

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
  }, [onViewModalOpen, selectedApplicant.id, selectedBucket, toast, user.uid]);

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
      <VStack width="100%" flex="1" overflowY="auto" overflowX="auto">
        <Alert status="warning" minHeight="80px" borderRadius="10px" mb="4" fontSize="16px">
          <AlertIcon />
          <AlertDescription>
            Only vectorized files are included in the applicant summary generated by the AI model, and currently only one file may be vectorized at a time.
            Vectorizing a file will delete the vectors for any other file.
            Support for multiple files will be added in a future version.
          </AlertDescription>
        </Alert>
        <FileDropzone onDrop={onDrop} disabled={uploadInProgress} />
        <FileTable
          documents={documents}
          vectorizeFile={vectorizeFile}
          unvectorizeFile={unvectorizeFile}
          vectorizeAllFiles={vectorizeAllFiles}
          unvectorizeAllFiles={unvectorizeAllFiles}
          deleteFile={deleteFile}
          viewFile={viewFile}
          vectorizingFiles={vectorizingFiles}
          vectorizeStatus={vectorizeStatus}
        />
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
      <ViewFileModal
        isOpen={isViewModalOpen}
        onClose={onViewModalClose}
        fileName={fileToView}
        fileContent={fileContent}
      />
      <UploadingFileModal
        isOpen={isUploadModalOpen}
        onClose={onUploadModalClose}
        fileName={uploadingFileName}
      />
      <DeletingFileModal
        isOpen={isDeleteInProgressModalOpen}
        onClose={onDeleteInProgressModalClose}
        fileName={deletingFileName}
      />
    </VStack>
  );
};

export default FileUploader;
