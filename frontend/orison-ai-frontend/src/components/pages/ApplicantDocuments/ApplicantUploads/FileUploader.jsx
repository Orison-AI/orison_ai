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
  useDisclosure, useToast, VStack, Button, Spinner, Center,
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
import { useApplicantContext } from "../../../../context/ApplicantContext";

const FileUploader = ({ }) => {
  const [user] = useAuthState(auth);
  const [documents, setDocuments] = useState([]);
  // Set "default" as the default tag and initialize state with it
  const [tags, setTags] = useState(["default"]);
  const [selectedTag, setSelectedTag] = useState("default");
  const [fileToOverwrite, setFileToOverwrite] = useState(null);
  // const [newTagName, setNewTagName] = useState('');

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
  const { selectedApplicant } = useApplicantContext();
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchApplicantData = useCallback(async () => {
    if (user && selectedApplicant) {
      // Use switch-case to assign file names based on visaCategory
      let templateFileName;
      switch (selectedApplicant.visaCategory) {
        case "EB1":
          templateFileName = "eb1_a_questionnaire";
          break;
        case "O1":
          templateFileName = "eb1_a_questionnaire";
          break;
        case "EB2":
          templateFileName = "eb1_a_questionnaire";
          break;
        default:
          templateFileName = "eb1_a_questionnaire";
      }

      try {
        // Fetch tags from the templates collection
        const templateDocRef = doc(db, "templates", templateFileName);
        const templateDocSnap = await getDoc(templateDocRef);

        let templateTags = [];
        if (templateDocSnap.exists()) {
          const templateData = templateDocSnap.data();
          templateTags = templateData.tags || []; // Get tags from template
          setTags(templateTags);
          
          // Set selectedTag to the first available tag from template, or "default" if none available
          if (templateTags.length > 0 && selectedTag === "default") {
            console.log(`Auto-selecting tag from template: ${templateTags[0]} (available tags: ${templateTags.join(', ')})`);
            setSelectedTag(templateTags[0]);
          }
        } else {
          console.warn("Template document does not exist.");
        }

        // Fetch applicant data
        const docRef = doc(db, "applicants", selectedApplicant.id);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
          const data = docSnap.data();

          // let applicantTags = data.customTags;
          // // Initialize customTags with templateTags if not present
          // if (!applicantTags || applicantTags.length === 0) {
          //   applicantTags = templateTags.length > 0 ? templateTags : ["default"];
          //   await updateDoc(docRef, { customTags: applicantTags });
          //   console.log("Initialized customTags with templateTags.");
          // }

          // Update state
          setVectorizedFiles(data.vectorized_files || []);
          // setTags(applicantTags);
        } else {
          console.warn("Applicant document does not exist.");
        }
      } catch (error) {
        console.error("Error fetching applicant data or tags:", error);
        setTags(["default"]); // Fallback to default in case of an error
      }
    }
  }, [user, selectedApplicant]);

  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      console.log('User ID:', user.uid);
      console.log('Applicant ID:', selectedApplicant.id);
      console.log('Selected Tag:', selectedTag);

      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/`;
      console.log('Fetching documents from path:', filePath);
      const storage = getStorage();
      const listRef = ref(storage, filePath);

      try {
        const res = await listAll(listRef);
        console.log('Found items in storage:', res.items.length);
        res.items.forEach(item => console.log('File:', item.name));
        
        const vectorizedSnap = await getDoc(doc(db, "applicants", selectedApplicant.id));
        const currentVectorized = vectorizedSnap.exists() ? vectorizedSnap.data().vectorized_files || [] : [];
        console.log('Vectorized files from Firestore:', currentVectorized);

        const docs = res.items.map(itemRef => ({
          fileName: itemRef.name,
          vectorized: currentVectorized.includes(itemRef.name),
        }));
        console.log('Setting documents from storage:', docs);
        setDocuments(docs);
              } catch (error) {
          console.error("Error fetching documents:", error);
        }
        
        // Always check subfolders to see what's actually there
        try {
          console.log('Checking all subfolders to see what files exist...');
          const basePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/`;
          const baseRef = ref(storage, basePath);
          const baseRes = await listAll(baseRef);
          console.log('Base path items:', baseRes.items);
          console.log('Base path prefixes:', baseRes.prefixes);
          
          // Check if there are any files in subfolders
          for (const prefix of baseRes.prefixes) {
            const subRes = await listAll(prefix);
            console.log(`Files in ${prefix.fullPath}:`, subRes.items.map(item => item.name));
          }
        } catch (subError) {
          console.error("Error checking subfolders:", subError);
        }
    } else {
      console.error("User, selectedApplicant, or selectedTag is undefined.");
    }
  }, [user, selectedApplicant, selectedTag]);

  // First useEffect: Load tags and set selectedTag
  useEffect(() => {
    const fetchData = async () => {
      await fetchApplicantData();
    };

    // Ensure selectedTag remains stable
    if (selectedTag !== "default" && !tags.includes(selectedTag)) {
      console.warn(`Resetting selectedTag to default. Found: ${selectedTag}`);
      setSelectedTag("default");
    }

    fetchData();
  }, [user, selectedApplicant, fetchApplicantData]);

  // Second useEffect: Fetch documents after selectedTag is properly set
  useEffect(() => {
    console.log('selectedTag changed to:', selectedTag);
    if (selectedTag && selectedTag !== "default") {
      console.log('Fetching documents for tag:', selectedTag);
      fetchDocuments();
    }
  }, [selectedTag, fetchDocuments]);


  useEffect(() => {
    if (vectorizeStatus === 'success') {
      fetchApplicantData(); // Refetch data after successful vectorization
    }
  }, [vectorizeStatus, fetchApplicantData]);

  const onDrop = async (acceptedFiles) => {
    const storage = getStorage();
    console.log('Uploading files with selectedTag:', selectedTag);

    for (const file of acceptedFiles) {
      const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/${file.name}`;
      console.log('Uploading file to path:', filePath);
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

  const deleteAllFiles = async () => {
    if (user && selectedApplicant) {
      try {
        setIsProcessing(true); // Block the UI

        const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${selectedTag}/`;
        const storage = getStorage();
        const listRef = ref(storage, filePath);

        // Fetch and delete all files in the selected tag
        const res = await listAll(listRef);

        for (const fileRef of res.items) {
          const fileName = fileRef.name;

          // Delete file vectors and the actual file
          await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileName);
          await deleteObject(fileRef);

          // Update local state
          setDocuments((prevDocuments) =>
            prevDocuments.filter((doc) => doc.fileName !== fileName)
          );
        }

        toast({
          title: "Delete All Completed",
          description: "All files have been successfully deleted.",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } catch (error) {
        console.error("Error deleting all files:", error);
        toast({
          title: "Error",
          description: "An error occurred while deleting files.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsProcessing(false); // Re-enable the UI
      }
    }
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

      // Delete file from storage
      await deleteObject(storageRef);
      console.log('File deleted from storage successfully');

      // Try to delete vectors, but don't fail the whole operation if this fails
      try {
        await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileToDelete);
        console.log('File vectors deleted successfully');
      } catch (vectorError) {
        console.warn('Failed to delete file vectors, but file was deleted:', vectorError.message);
        // Don't show error toast for vector deletion failure
      }

      toast({
        title: 'File Deleted',
        description: `File ${fileToDelete} deleted successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Try to refresh documents, but don't fail if this errors
      try {
        await fetchDocuments();
      } catch (fetchError) {
        console.warn('Failed to refresh documents after delete:', fetchError.message);
      }
      
      onDeleteModalClose();
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
      try {
        console.log('Vectorizing file:', fileName);
        console.log('User ID:', user.uid);
        console.log('Applicant ID:', selectedApplicant.id);
        console.log('Selected Tag:', selectedTag);
        
        setIsProcessing(true); // Block the UI during vectorization

        const docRef = doc(db, "applicants", selectedApplicant.id);

        // Call the vectorization function
        await vectorizeFiles(user.uid, selectedApplicant.id, selectedTag, fileName);

        // Update Firestore with the vectorized file
        const docSnap = await getDoc(docRef);
        const currentVectorized = docSnap.exists() ? docSnap.data().vectorized_files || [] : [];

        if (!currentVectorized.includes(fileName)) {
          await updateDoc(docRef, {
            vectorized_files: [...currentVectorized, fileName],
          });
        }

        // Update the documents state immediately
        setDocuments((prevDocuments) =>
          prevDocuments.map((doc) =>
            doc.fileName === fileName
              ? { ...doc, vectorized: true } // Mark as vectorized
              : doc
          )
        );

        toast({
          title: "Vectorization Completed",
          description: `${fileName} vectorized successfully.`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } catch (error) {
        console.error("Error vectorizing file:", error);
        console.error("Error details:", {
          message: error.message,
          stack: error.stack,
          fileName,
          selectedTag,
          user: user?.uid,
          applicant: selectedApplicant?.id
        });
        toast({
          title: "Error",
          description: `An error occurred while vectorizing ${fileName}.`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsProcessing(false); // Re-enable UI when done
      }
    }
  }, [user, selectedApplicant, selectedTag, toast]);


  const vectorizeAllFiles = useCallback(async () => {
    if (user && selectedApplicant) {
      try {
        setIsProcessing(true); // Block the UI during processing

        const docRef = doc(db, "applicants", selectedApplicant.id);
        const docSnap = await getDoc(docRef);
        const vectorizedFiles = docSnap.exists() ? docSnap.data().vectorized_files || [] : [];

        // Filter files that are not yet vectorized
        const nonVectorizedFiles = documents
          .filter((doc) => !vectorizedFiles.includes(doc.fileName))
          .map((doc) => doc.fileName);

        for (const fileName of nonVectorizedFiles) {
          await vectorizeFile(fileName);

          // Update the state immediately after each file
          setDocuments((prevDocuments) =>
            prevDocuments.map((doc) =>
              doc.fileName === fileName
                ? { ...doc, vectorized: true } // Mark as vectorized
                : doc
            )
          );
        }

        toast({
          title: "Vectorize All Completed",
          description: "All non-vectorized files have been processed.",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } catch (error) {
        console.error("Error during vectorize all:", error);
        toast({
          title: "Error",
          description: "An error occurred while processing all files.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsProcessing(false); // Re-enable UI when done
      }
    }
  }, [user, selectedApplicant, documents, vectorizeFile, toast]);

  const unvectorizeFile = async (fileName) => {
    if (user && selectedApplicant) {
      try {
        setIsProcessing(true); // Block the UI during the process

        // Delete file vectors from backend
        await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileName);

        // Update Firestore to remove the file from the `vectorized_files`
        const docRef = doc(db, 'applicants', selectedApplicant.id);
        const docSnap = await getDoc(docRef);
        const vectorizedFiles = docSnap.exists() ? docSnap.data().vectorized_files || [] : [];

        if (vectorizedFiles.includes(fileName)) {
          await updateDoc(docRef, {
            vectorized_files: vectorizedFiles.filter((file) => file !== fileName),
          });
        }

        // Update the local state to reflect the unvectorized file
        setDocuments((prevDocuments) =>
          prevDocuments.map((doc) =>
            doc.fileName === fileName
              ? { ...doc, vectorized: false } // Set the file as unvectorized
              : doc
          )
        );

        toast({
          title: 'Unvectorization Completed',
          description: `${fileName} has been unvectorized successfully.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } catch (error) {
        console.error('Error unvectorizing file:', error);
        toast({
          title: 'Error',
          description: `An error occurred while unvectorizing ${fileName}.`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsProcessing(false); // Re-enable the UI
      }
    }
  };

  const unvectorizeAllFiles = async () => {
    if (user && selectedApplicant) {
      try {
        setIsProcessing(true); // Block the UI during processing

        const docRef = doc(db, 'applicants', selectedApplicant.id);
        const docSnap = await getDoc(docRef);
        const vectorizedFiles = docSnap.exists() ? docSnap.data().vectorized_files || [] : [];

        for (const fileName of vectorizedFiles) {
          // Delete file vectors from backend
          await deleteFileVectors(user.uid, selectedApplicant.id, selectedTag, fileName);

          // Update Firestore to remove the file from `vectorized_files`
          await updateDoc(docRef, {
            vectorized_files: vectorizedFiles.filter((file) => file !== fileName),
          });

          // Update the local state for each file as it is processed
          setDocuments((prevDocuments) =>
            prevDocuments.map((doc) =>
              doc.fileName === fileName
                ? { ...doc, vectorized: false } // Set the file as unvectorized
                : doc
            )
          );
        }

        toast({
          title: 'Unvectorize All Completed',
          description: 'All files have been unvectorized successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } catch (error) {
        console.error('Error unvectorizing all files:', error);
        toast({
          title: 'Error',
          description: 'An error occurred while unvectorizing all files.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsProcessing(false); // Re-enable the UI
      }
    }
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
      <HStack width="100%" fontSize="24px" spacing={4} alignItems="center">
        <Text width="100%">Applicant Files</Text>

        {/* Tag Label and Dropdown */}
        <HStack spacing={2} alignItems="center" width="50%">
          <Text fontSize="lg" color="gray.300" flexShrink={0}>Select Tag:</Text>
          <Select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            color="blue.100"
            width="250px" /* Widen the dropdown */
          >
            {tags.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </Select>
        </HStack>

        {/* Input Box for Tag Name */}
        {/* <Box minWidth="200px">
          <input
            type="text"
            maxLength="30"
            placeholder="New tag name"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            style={{ padding: "6px", fontSize: "16px", borderRadius: "5px", width: "100%" }}
          />
        </Box> */}

        {/* Add Button */}
        {/* <Button
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
        </Button> */}

        {/* Remove Button */}
        {/* <Button
          colorScheme="red"
          onClick={async () => {
            if (
              selectedTag !== "default" &&
              window.confirm(
                `Delete all files and their vectors in the "${selectedTag}" tag?`
              )
            ) {
              try {
                setIsProcessing(true); // Block the screen and dim the UI

                // Call the function to delete all vectors
                await deleteAllFileVectorsInTag();

                // Update the tags in state and Firestore
                const updatedTags = tags.filter((tag) => tag !== selectedTag);
                setTags(updatedTags);
                setSelectedTag("default"); // Reset to "default" if the selected tag is deleted

                const docRef = doc(db, "applicants", selectedApplicant.id);
                await updateDoc(docRef, { customTags: updatedTags });

                toast({
                  title: "Tag Deleted",
                  description: `Tag "${selectedTag}" and all associated file vectors were deleted.`,
                  status: "success",
                  duration: 5000,
                  isClosable: true,
                });
              } catch (error) {
                console.error("Error deleting tag and vectors:", error);
                toast({
                  title: "Error",
                  description: "An error occurred while deleting the tag.",
                  status: "error",
                  duration: 5000,
                  isClosable: true,
                });
              } finally {
                setIsProcessing(false); // Re-enable the screen
              }
            }
          }}
          isDisabled={selectedTag === "default"} // Disable deletion for "default" tag
        >
          Del
        </Button> */}
      </HStack>

      {isProcessing && (
        <Center
          position="absolute"
          top="0"
          left="0"
          width="100%"
          height="100%"
          bg="rgba(0, 0, 0, 0.5)"
          zIndex="overlay"
        >
          <Spinner size="xl" color="white" />
          <Text mt={4} color="white" fontSize="lg">
            Processing files. Please wait...
          </Text>
        </Center>
      )}

      {/* Rest of the component remains unchanged */}
      <VStack width="100%" flex="1" overflowY="auto" overflowX="auto">
        <Alert status="warning" minHeight="80px" borderRadius="10px" mb="4" fontSize="16px">
          <AlertIcon />
          <AlertDescription>
            - Use tags to help AI find relevant information. Match documents to the right tags. Not all tags may apply. <br />
            {/* - Add/Del tags, but update the questionnaire with new tags. AI will not use your documents otherwise. <br /> */}
            - Vectorize files after upload for AI search. Avoid uploading large files (&gt;1000 pages or 50 MB). <br />
            - Vectorization may take an estimated 1 second per 10 pages. You may switch windows but donot close this window. <br />
            - Supported extensions: .txt, .json, .md, .html, .csv, .pdf, .docx, .doc, .docs, .pptx, .xls, .xlsx, .xml <br />
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
          deleteAllFiles={deleteAllFiles}
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