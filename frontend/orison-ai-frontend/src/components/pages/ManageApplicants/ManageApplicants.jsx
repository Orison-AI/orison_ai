// ./components/pages/ManageApplicants/ManageApplicants.jsx

// React
import React, { useEffect, useState, useRef } from 'react';

// Firebase
import { useAuthState } from 'react-firebase-hooks/auth';
import {
  addDoc, collection, deleteDoc, doc,
  onSnapshot, query, setDoc, where,
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
  const emailRef = useRef();
  const statusRef = useRef();

  // Set the applicants list
  useEffect(() => {
    let unsubscribe = () => {};

    async function fetchApplicants() {
      if (user) {
        const q = query(collection(db, "applicants"), where("user_id", "==", user.uid));

        unsubscribe = onSnapshot(
          q, (snapshot) => {
            const newApplicants = snapshot.docs
              .map(doc => ({
                id: doc.id,
                ...doc.data()
              }));
            setApplicants(newApplicants);
          },
          (error) => {
            console.error("Error fetching applicants:", error);
          }
        );
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
    try {
      const newDoc = await addDoc(collection(db, "applicants"), {
        user_id: user.uid,
        name: "",
        email: "",
        status: "",
      });
      startEdit(newDoc.id);
    } catch (error) {
      console.error("Failed to add new applicant:", error);
    }
  };

  const startEdit = (id) => setEditId(id);
  const cancelEdit = () => setEditId(null);

  const saveEdit = async (applicant) => {
    try {
      if (user) {
        await setDoc(doc(collection(db, "applicants"), applicant.id), {
          user_id: user.uid,
          name: nameRef.current.value || "",
          email: emailRef.current.value || "",
          status: statusRef.current.value || "",
        }, { merge: true });
      }
    } catch (error) {
      console.error("Failed to add new applicant:", error);
    }
    setEditId(null);
  };

  const deleteApplicant = async (applicant) => {
    try {
      if (selectedApplicant && selectedApplicant.id === applicant.id) {
        setSelectedApplicant(null);
      }
      await deleteDoc(doc(collection(db, "applicants"), applicant.id));
      onClose(); // Only close the modal if deletion is successful
    } catch (error) {
      console.error("Failed to delete applicant:", error);
    }
  };

  const confirmDelete = (applicant) => {
    setApplicantToDelete(applicant);
    onOpen();
  };

  const handleKeyDown = (e, applicant) => {
    if (e.key === 'Enter') {
      saveEdit(applicant);
    }
  };

  const viewDocs = (applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(Views.APPLICANT_DOCUMENTS);
  }

  const viewInformatics = (applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(Views.APPLICANT_INFORMATICS);
  }

  return (
    <Box width="100%">
      <Text fontSize="3vh" m="2vh" mb="4vh" color="gray.400">Manage Applicants</Text>
      <Center>
        <Box overflowX="auto" maxWidth="90%" border="1px" borderColor="gray.600" borderRadius="1vh">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Email</Th>
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
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : applicant.name}
                  </Td>
                  <Td minWidth="20vh">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.email} 
                        ref={emailRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : applicant.email}
                  </Td>
                  <Td minWidth="20vh">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.status}
                        ref={statusRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : applicant.status}
                  </Td>
                  <Td minWidth="35vh">
                    {editId === applicant.id ? (
                      <>
                        <IconButton icon={<CheckIcon />} onClick={() => saveEdit(applicant)} colorScheme="green" mr="0.5vh" />
                        <IconButton icon={<CloseIcon />} onClick={cancelEdit} colorScheme="red" />
                      </>
                    ) : (
                      <>
                        <IconButton icon={<EditIcon />} onClick={() => startEdit(applicant.id)} colorScheme="blue" />
                      </>
                    )}
                    <Button ml="1.0vh" onClick={() => viewDocs(applicant)}>Documents</Button>
                    <Button ml="0.5vh" onClick={() => viewInformatics(applicant)}>Informatics</Button>
                  </Td>
                  <Td isNumeric>
                    <IconButton icon={<CloseIcon />} onClick={() => confirmDelete(applicant)} colorScheme="red" variant="ghost" />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </Center>
      <Center>
        <Button mt="2vh" colorScheme="blue" onClick={addNewApplicant}>Add New Applicant</Button>
      </Center>
      <DeleteApplicantModal
        isOpen={isOpen}
        onClose={onClose}
        onDelete={() => deleteApplicant(applicantToDelete)}
        applicant={applicantToDelete}
      />
    </Box>
  );
};

export default ManageApplicants;
