// ./components/pages/UploadDocuments.jsx

// React
import React from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { collection, doc, setDoc } from 'firebase/firestore';

// Chakra
import { HStack, Spacer, Text, VStack, useToast } from '@chakra-ui/react';

// Dropzone
import { useDropzone } from 'react-dropzone';

// Internal
import { db, auth } from '../../firebaseConfig';

const UploadDocuments = ({ selectedApplicant }) => {
  const [user] = useAuthState(auth);
  const toast = useToast();

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
    </VStack>
  );
}

export default UploadDocuments;
