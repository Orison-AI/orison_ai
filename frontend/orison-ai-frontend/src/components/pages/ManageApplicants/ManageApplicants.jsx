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
  Table, Thead, Tbody, Tr, Th, Td,
  useDisclosure, Menu, MenuButton, MenuItem, MenuList
} from '@chakra-ui/react';
import { EditIcon, CloseIcon, CheckIcon, ChevronDownIcon } from '@chakra-ui/icons';

// Internal
import { db, auth } from '../../../common/firebaseConfig';
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

  // Set the applicants list
  useEffect(() => {
    let unsubscribe = () => { };

    async function fetchApplicants() {
      if (user) {
        const q = query(collection(db, "applicants"), where("attorney_id", "==", user.uid));

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
        attorney_id: user.uid,
        name: "",
        email: "",
        files: [],
        vectorized_files: [],
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
          attorney_id: user.uid,
          name: nameRef.current.value || "",
          email: emailRef.current.value || "",
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

  // Handle navigation to views when menu items are clicked
  const handleNavigate = (view, applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(view);
  };

  return (
    <Box className="oai-manage-view" width="100%">
      <Center className="oai-manage-table-center">
        <Box className="oai-manage-table-container" overflowX="auto" minWidth="60%" maxWidth="90%" border="1px" borderColor="gray.600" borderRadius="8px">
          <Table className="oai-manage-table" variant="simple">
            <Thead className="oai-manage-thead">
              <Tr>
                <Th>Name</Th>
                <Th>Email</Th>
                <Th>Visa Type</Th>
                <Th></Th>
              </Tr>
            </Thead>
            <Tbody className="oai-manage-tbody">
              {applicants.map(applicant => (
                <Tr key={applicant.id}>
                  <Td whiteSpace="nowrap">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.name}
                        ref={nameRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : applicant.name}
                  </Td>
                  <Td whiteSpace="nowrap">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.email}
                        ref={emailRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : applicant.email}
                  </Td>
                  <Td isNumeric whiteSpace="nowrap">
                    {editId === applicant.id ? (
                      <>
                        <IconButton icon={<CheckIcon />} onClick={() => saveEdit(applicant)} colorScheme="green" mr="4px" />
                        <IconButton icon={<CloseIcon />} onClick={cancelEdit} colorScheme="red" />
                      </>
                    ) : (
                      <>
                        <IconButton icon={<EditIcon />} onClick={() => startEdit(applicant.id)} colorScheme="blue" />
                      </>
                    )}

                    {/* Dropdown Menu for all options */}
                    <Menu>
                      <MenuButton as={Button} rightIcon={<ChevronDownIcon />} ml="8px">
                        AI ToolBox
                      </MenuButton>
                      <MenuList>
                        <MenuItem onClick={() => handleNavigate(Views.APPLICANT_DOCUMENTS, applicant)}>
                          Documents
                        </MenuItem>
                        <MenuItem onClick={() => handleNavigate(Views.QUESTIONAIRE, applicant)}>
                          Questionnaire
                        </MenuItem>
                        <MenuItem onClick={() => handleNavigate(Views.APPLICANT_SUMMARIZATION, applicant)}>
                          Summarization
                        </MenuItem>
                        <MenuItem onClick={() => handleNavigate(Views.APPLICANT_SUMMARIZATION, applicant)}>
                          EvidenceLetter
                        </MenuItem>
                        <MenuItem onClick={() => handleNavigate(Views.DOCASSIST, applicant)}>
                          DocAssist
                        </MenuItem>
                      </MenuList>
                    </Menu>

                    <IconButton ml="8px" icon={<CloseIcon />} onClick={() => confirmDelete(applicant)} colorScheme="red" variant="ghost" />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </Center>
      <Center className="oai-manage-addnewapp-button-center">
        <Button mt="16px" colorScheme="blue" onClick={addNewApplicant}>Add New Applicant</Button>
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
