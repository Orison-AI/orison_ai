// ./components/pages/UploadDocuments.jsx

// React
import React, { useCallback, useEffect, useState } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import {
  getStorage, ref, uploadBytes, getDownloadURL, deleteObject,
} from 'firebase/storage';
import {
  collection, doc, setDoc, getDocs, deleteDoc
} from 'firebase/firestore';

// Chakra
import {
  HStack, IconButton,
  Table, Thead, Tbody, Tr, Th, Td,
  Text, useToast, VStack,
} from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';

// Dropzone
import { useDropzone } from 'react-dropzone';

// Internal
import { db, auth } from '../../firebaseConfig';

const UploadDocuments = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const toast = useToast();
  const [documents, setDocuments] = useState([]);

  const fetchDocuments = useCallback(async () => {
    if (user && selectedApplicant) {
      const applicantsCollection = collection(db, 'attorneys', user.uid, 'applicants', selectedApplicant.id, 'files');
      const querySnapshot = await getDocs(applicantsCollection);
      const docs = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setDocuments(docs);
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
      let downloadURL = null;
  
      try {
        // Upload the file to Firebase Storage
        const fileSnapshot = await uploadBytes(storageRef, file);
  
        // Get the URL of the uploaded file
        downloadURL = await getDownloadURL(fileSnapshot.ref);
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
  
      try {
        // Save the file reference in Firestore
        const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");
        const fileRef = doc(applicantsCollection, selectedApplicant.id, "files", file.name);
        await setDoc(fileRef, { url: downloadURL }, { merge: true });
  
        toast({
          title: 'File Metadata Updated',
          description: `File ${file.name} URL saved to database.`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });

        // Fetch updated documents
        fetchDocuments();
      } catch (error) {
        console.error(`Error saving metadata for file: ${error.message}`);
        toast({
          title: 'Error Uploading File',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    });
  };

  const deleteFile = async (fileName, fileUrl) => {
    const storage = getStorage();
    const filePath = `documents/attorneys/${user.uid}/applicants/${selectedApplicant.id}/${fileName}`;
    const storageRef = ref(storage, filePath);

    try {
      // Delete the file from Firebase Storage
      await deleteObject(storageRef);

      // Delete the file reference from Firestore
      const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");
      const fileRef = doc(applicantsCollection, selectedApplicant.id, "files", fileName);
      await deleteDoc(fileRef);

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

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <VStack height="100%" width="100%" padding="2vh" fontSize="4vh">
      <HStack width="100%">
        <Text fontSize="3vh" m="2vh" mb="4vh" color="gray.400">Documents</Text>
        {/* <Spacer /> */}
        <Text fontSize="3vh" m="2vh" mb="4vh" color="green.300" as="strong">
          {selectedApplicant ? selectedApplicant.name : "No applicant selected"}
        </Text>
      </HStack>
      <VStack {...getRootProps()} border="2px dashed gray" padding="20px" width="50%" marginTop="4vh">
        <input {...getInputProps()} />
        {
          isDragActive ?
            <Text>Drop the files here...</Text> :
            <Text>Drag files here or click to select files</Text>
        }
      </VStack>
      <Table variant="simple" width="50%" marginTop="4vh">
        <Thead>
          <Tr>
            <Th>File Name</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody fontSize="2vh">
          {documents.map(doc => (
            <Tr key={doc.id}>
              <Td>{doc.id}</Td>
              <Td isNumeric>
                <IconButton
                  icon={<CloseIcon />}
                  colorScheme="red"
                  variant="ghost"
                  onClick={() => deleteFile(doc.id, doc.url)}
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </VStack>
  );
}

export default UploadDocuments;
