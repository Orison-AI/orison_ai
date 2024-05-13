// ./components/pages/ManageApplicants/ManageApplicants.jsx

// React
import React, { useEffect, useState, useRef } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import {
  addDoc, collection, deleteDoc, doc, onSnapshot, setDoc,
} from "firebase/firestore";

// Chakra
import {
  Box, Button, Center, IconButton, Input,
  Table, Thead, Tbody, Tr, Th, Td, Text,
  useDisclosure,
} from '@chakra-ui/react';
import { EditIcon, CloseIcon, CheckIcon } from '@chakra-ui/icons';

// Internal
import { db, auth } from '../../../firebaseConfig';
import Views from '../../../common/views';
import DeleteApplicantModal from './DeleteApplicantModal';

const ManageApplicants = ({
  applicants, setApplicants,
  selectedApplicant, setSelectedApplicant,
  setCurrentView,
}) => {
  const [editId, setEditId] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [applicantToDelete, setApplicantToDelete] = useState(null);
  const [user] = useAuthState(auth);

  // Refs for edit fields
  const nameRef = useRef();
  const visaTypeRef = useRef();
  const statusRef = useRef();

  // Set the applicants list
  useEffect(() => {
    let unsubscribe = () => {};

    async function fetchApplicants() {
      if (user) {
        const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");

        unsubscribe = onSnapshot(applicantsCollection, (snapshot) => {
          const newApplicants = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
          }));
          setApplicants(newApplicants);
        }, (error) => {
          console.error("Error fetching applicants:", error);
        });
      }
    }
  
    // Call the async function
    fetchApplicants();

    // Return the cleanup function
    return () => {
      unsubscribe();
    };
  }, [user, setApplicants]);

  const addNewApplicant = async () => {
    const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");
    try {
      const newDoc = await addDoc(applicantsCollection, {
        name: "",
        visaType: "",
        status: "",
      });
      startEdit(newDoc.id);
    } catch (error) {
      console.error("Failed to add new applicant:", error);
    }
  };

  const startEdit = (id) => setEditId(id);
  const cancelEdit = () => setEditId(null);

  const saveEdit = async (id) => {
    const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");
    try {
      await setDoc(doc(applicantsCollection, id), {
        name: nameRef.current.value,
        visaType: visaTypeRef.current.value,
        status: statusRef.current.value,
      }, { merge: true });
    } catch (error) {
      console.error("Failed to add new applicant:", error);
    }
    setEditId(null);
  };

  const deleteApplicant = async (id) => {
    const applicantsCollection = collection(db, "attorneys", user.uid, "applicants");
    try {
      if (selectedApplicant.id === id) {
        setSelectedApplicant(null);
      }
      await deleteDoc(doc(applicantsCollection, id));
      onClose(); // Only close the modal if deletion is successful
    } catch (error) {
      console.error("Failed to delete applicant:", error);
    }
  };

  const confirmDelete = (applicant) => {
    setApplicantToDelete(applicant);
    onOpen();
  };

  const handleKeyDown = (e, id) => {
    if (e.key === 'Enter') {
      saveEdit(id);
    }
  };

  const uploadDocsForApplicant = (applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(Views.UPLOAD_DOCUMENTS);
  }

  const screenApplicant = (applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(Views.SCREENING);
  }

  const reviewApplicant = (applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(Views.STORY_BUILDER);
  }

  return (
    <Box width="100%">
      <Text fontSize="3vh" m="2vh" mb="4vh" color="gray.400">Manage Applicants</Text>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Visa Type</Th>
            <Th>Status</Th>
            <Th>Actions</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody>
          {applicants.map(applicant => (
            <Tr key={applicant.id}>
              <Td minWidth="20vh">
                {editId === applicant.id ? (
                  <Input
                    defaultValue={applicant.name}
                    ref={nameRef}
                    onKeyDown={(e) => handleKeyDown(e, applicant.id)}
                  />
                ) : applicant.name}
              </Td>
              <Td minWidth="20vh">
                {editId === applicant.id ? (
                  <Input
                    defaultValue={applicant.visaType} 
                    ref={visaTypeRef}
                    onKeyDown={(e) => handleKeyDown(e, applicant.id)}
                  />
                ) : applicant.visaType}
              </Td>
              <Td minWidth="20vh">
                {editId === applicant.id ? (
                  <Input
                    defaultValue={applicant.status}
                    ref={statusRef}
                    onKeyDown={(e) => handleKeyDown(e, applicant.id)}
                  />
                ) : applicant.status}
              </Td>
              <Td minWidth="35vh">
                {editId === applicant.id ? (
                  <>
                    <IconButton icon={<CheckIcon />} onClick={() => saveEdit(applicant.id)} colorScheme="green" mr="0.5vh" />
                    <IconButton icon={<CloseIcon />} onClick={cancelEdit} colorScheme="red" />
                  </>
                ) : (
                  <>
                    <IconButton icon={<EditIcon />} onClick={() => startEdit(applicant.id)} colorScheme="blue" />
                  </>
                )}
                <Button ml="1.0vh" onClick={() => uploadDocsForApplicant(applicant)}>Upload</Button>
                <Button ml="0.5vh" onClick={() => screenApplicant(applicant)}>Screen</Button>
                <Button ml="0.5vh" onClick={() => reviewApplicant(applicant)}>Review</Button>
              </Td>
              <Td isNumeric>
                <IconButton icon={<CloseIcon />} onClick={() => confirmDelete(applicant)} colorScheme="red" variant="ghost" />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
      <Center>
        <Button mt="2vh" colorScheme="blue" onClick={addNewApplicant}>Add New Applicant</Button>
      </Center>
      <DeleteApplicantModal
        isOpen={isOpen}
        onClose={onClose}
        onDelete={() => deleteApplicant(applicantToDelete.id)}
        applicant={applicantToDelete?.name}
      />
    </Box>
  );
};

export default ManageApplicants;
