// ./components/pages/ManageApplicants/ManageApplicants.jsx

// External
import React, { useState, useRef } from 'react';
import {
  Box, Button, Center, IconButton, Input,
  Table, Thead, Tbody, Tr, Th, Td,
  Text, useColorMode, useDisclosure,
} from '@chakra-ui/react';
import { EditIcon, CloseIcon, CheckIcon } from '@chakra-ui/icons';

// Internal
import Views from '../../../common/views';
import DeleteApplicantModal from './DeleteApplicantModal';

const ManageApplicants = ({applicants, setApplicants, setSelectedApplicant, setCurrentView}) => {
  const [editId, setEditId] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [applicantToDelete, setApplicantToDelete] = useState(null);
  const { colorMode } = useColorMode();

  const titleColor = colorMode === "light" ? "gray.400" : "gray.400";

  // Refs for edit fields
  const nameRef = useRef();
  const visaTypeRef = useRef();
  const statusRef = useRef();

  const startEdit = (id) => setEditId(id);
  const cancelEdit = () => setEditId(null);

  const saveEdit = (id) => {
    const updatedName = nameRef.current.value;
    const updatedVisaType = visaTypeRef.current.value;
    const updatedStatus = statusRef.current.value;
    setApplicants(applicants.map(applicant =>
      applicant.id === id ? { ...applicant, name: updatedName, visaType: updatedVisaType, status: updatedStatus } : applicant
    ));
    cancelEdit();
  };

  const handleKeyDown = (e, id) => {
    if (e.key === 'Enter') {
      saveEdit(id);
    }
  };

  const addNewApplicant = () => {
    cancelEdit(); // Ensure no other items are being edited
    const newApplicant = {
      id: Date.now(), // Using the current timestamp for a unique ID
      name: '',       // Initial empty value
      visaType: '',   // Initial empty value
      status: ''      // Initial empty value
    };
    setApplicants([...applicants, newApplicant]); // Add the new applicant to the state
    setEditId(newApplicant.id); // Set this new applicant to be in edit mode immediately
  };

  const deleteApplicant = (id) => {
    setApplicants(applicants.filter(applicant => applicant.id !== id));
    onClose();
  };

  const confirmDelete = (applicant) => {
    setApplicantToDelete(applicant);
    onOpen();
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
      <Text fontSize="2vh" m="2vh" mb="4vh" color={titleColor}>Manage Applicants</Text>
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
                <Button ml="0.5vh" onClick={() => uploadDocsForApplicant(applicant)}>Upload</Button>
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
