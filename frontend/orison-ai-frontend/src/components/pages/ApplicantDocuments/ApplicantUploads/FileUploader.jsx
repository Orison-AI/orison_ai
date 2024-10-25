// ./components/pages/ApplicantDocuments/ApplicantUploads/FileUploader.jsx

// React
import React, { useCallback, useState, useEffect } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../../common/firebaseConfig';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
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

const FileUploader = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const [documents, setDocuments] = useState([]);
  // Set "main" as the default tag and initialize state with it
  const [tags, setTags] = useState(["main"]);
  const [selectedTag, setSelectedTag] = useState("main");
  const [fileToOverwrite, setFileToOverwrite] = useState(null);
  const [newTagName, setNewTagName] = useState('');

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

  const fetchApplicantData = useCallback(async () => {
    if (user && selectedApplicant) {
      const docRef = doc(db, "applicants", selectedApplicant.id);
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        const data = docSnap.data();
        setVectorizedFiles(data.vectorized_files || []);
        setTags(data.customTags || ["main"]); // Set tags from Firestore, defaulting to "main" if empty
      }
    }
  }, [user, selectedApplicant]);


  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      console.log('User ID:', user.uid);
      console.log('Applicant ID:', selectedApplicant.id);
      console.log('Selected Tag:', selectedTag);

      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/`;
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
    } else {
      console.error("User, selectedApplicant, or selectedTag is undefined.");
    }
  }, [user, selectedApplicant, selectedTag, vectorizedFiles]);


  useEffect(() => {
    fetchApplicantData(); // Fetch both vectorized files and custom tags on component mount
  }, [fetchApplicantData]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments, selectedTag]);

  useEffect(() => {
    if (vectorizeStatus === 'success') {
      fetchApplicantData(); // Refetch data after successful vectorization
    }
  }, [vectorizeStatus, fetchApplicantData]);

  const onDrop = async (acceptedFiles) => {
    const storage = getStorage();

    for (const file of acceptedFiles) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/${file.name}`;
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
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/${fileToOverwrite.name}`;
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

  const deleteAllFileVectorsInTag = useCallback(async () => {
    if (user && selectedApplicant && selectedTag) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/`;
      const storage = getStorage();
      const listRef = ref(storage, filePath);

      try {
        const res = await listAll(listRef);
        const filesToDelete = res.items.map(itemRef => itemRef); // Get all file references

        for (const fileRef of filesToDelete) {
          const fileName = fileRef.name;
          console.log(`Deleting vectors for file: ${fileName}`);

          // First, delete the vectors for each file
          await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileName);

          // Then, delete the actual file from Firebase Storage
          await deleteObject(fileRef);
          console.log(`File ${fileName} deleted from storage.`);
        }

        console.log(`All vectors and files deleted for tag: ${selectedTag}`);
        toast({
          title: 'Success',
          description: `Vectors and files for all files in the "${selectedTag}" tag were deleted.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } catch (error) {
        console.error("Error deleting file vectors or files:", error);
        toast({
          title: 'Error',
          description: 'Error occurred while deleting file vectors and files.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } else {
      console.error("User, selectedApplicant, or selectedTag is undefined.");
    }
  }, [user, selectedApplicant, selectedTag]);



  const handleDeleteConfirm = async () => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/${fileToDelete}`;
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

      await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileToDelete);
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
        // Call the vectorization API (or function)
        await vectorizeFiles(user.uid, selectedApplicant.id, selectedTag, fileName);

        // Fetch current vectorized files from Firestore
        const docRef = doc(db, 'applicants', selectedApplicant.id);
        const docSnap = await getDoc(docRef);
        let currentVectorizedFiles = [];

        if (docSnap.exists()) {
          currentVectorizedFiles = docSnap.data().vectorized_files || [];
        }

        // Add the new file to the vectorized_files list if it's not already there
        if (!currentVectorizedFiles.includes(fileName)) {
          const updatedVectorizedFiles = [...currentVectorizedFiles, fileName];

          // Update the vectorized_files field in Firestore
          await updateDoc(docRef, {
            vectorized_files: updatedVectorizedFiles
          });
        }

        // Show success toast
        toast({
          title: 'Vectorization Completed',
          description: `Vectorization for ${fileName} has completed successfully.`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        setVectorizeStatus('success');

      } catch (error) {
        // Show error toast if vectorization or Firestore update fails
        toast({
          title: 'Vectorization Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        setVectorizeStatus('error');

      } finally {
        // Remove the file from the vectorizing state
        setVectorizingFiles((prev) => prev.filter((file) => file !== fileName));
      }
    }
  }, [user, selectedApplicant, selectedTag, toast]);


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
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/${fileName}`;
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
  }, [onViewModalOpen, selectedApplicant.id, selectedTag, toast, user.uid]);

  return (
    <VStack width="100%" flex="1" mt="20px" overflowY="auto" overflowX="auto">
      <HStack width="100%" fontSize="24px" spacing={4}>
        <Text width="100%">Applicant Files</Text>
        <Box minWidth="200px" fontSize="24px">
          <Select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            color="blue.100"
          >
            {tags.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </Select>
        </Box>

        {/* Input Box for Tag Name */}
        <Box minWidth="200px">
          <input
            type="text"
            maxLength="30"
            placeholder="New tag name"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            style={{ padding: "6px", fontSize: "16px", borderRadius: "5px", width: "100%" }}
          />
        </Box>

        {/* Add Button */}
        <Button
          colorScheme="teal"
          onClick={async () => {
            if (newTagName && !tags.includes(newTagName)) {
              const updatedTags = [...tags, newTagName];
              setTags(updatedTags);
              setSelectedTag(newTagName);

              // Update Firestore with the new tag list
              const docRef = doc(db, "applicants", selectedApplicant.id);
              await updateDoc(docRef, { customTags: updatedTags });

              toast({
                title: 'Tag Added',
                description: `Tag "${newTagName}" added successfully.`,
                status: 'success',
                duration: 3000,
                isClosable: true,
              });
              setNewTagName(''); // Clear input after adding
            }
          }}
        >
          Add
        </Button>

        {/* Remove Button */}
        <Button
          colorScheme="red"
          onClick={async () => {
            if (selectedTag !== "main" && window.confirm(`Delete all files and their vectors in the "${selectedTag}" tag?`)) {
              await deleteAllFileVectorsInTag(); // Call the function to delete vectors
              const updatedTags = tags.filter((tag) => tag !== selectedTag);
              setTags(updatedTags);
              setSelectedTag("main"); // Reset to "main" if the selected tag is deleted

              // Update Firestore with the updated tag list
              const docRef = doc(db, "applicants", selectedApplicant.id);
              await updateDoc(docRef, { customTags: updatedTags });

              toast({
                title: 'Tag Deleted',
                description: `Tag "${selectedTag}" and all associated file vectors were deleted.`,
                status: 'success',
                duration: 5000,
                isClosable: true,
              });
            }
          }}
          isDisabled={selectedTag === "main"} // Disable deletion for "main" tag
        >
          Del
        </Button>
      </HStack>


      {/* Rest of the component remains unchanged */}
      <VStack width="100%" flex="1" overflowY="auto" overflowX="auto">
        <Alert status="warning" minHeight="80px" borderRadius="10px" mb="4" fontSize="16px">
          <AlertIcon />
          <AlertDescription>
            Only vectorized files are included in the applicant summary generated by the AI model, and currently only one file may be vectorized at a time. Vectorizing a file will delete the vectors for any other file. Support for multiple files will be added in a future version.
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

      {/* Modals */}
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

}
export default FileUploader;