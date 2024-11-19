import React, { useEffect, useState, useRef } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  onSnapshot,
  query,
  setDoc,
  where,
  updateDoc,
} from "firebase/firestore";
import {
  Box,
  Button,
  Center,
  IconButton,
  Input,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useDisclosure,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Select,
  Text,
} from "@chakra-ui/react";
import { EditIcon, CloseIcon, CheckIcon, ChevronDownIcon } from "@chakra-ui/icons";
import { db, auth } from "../../../common/firebaseConfig";
import Views from "../../../common/views";
import DeleteApplicantModal from "./DeleteApplicantModal";

const visaCategories = ["EB1", "O1", "EB2"]; // Predefined visa categories

const ManageApplicants = ({
  applicants,
  setApplicants,
  selectedApplicant,
  setSelectedApplicant,
  setCurrentView,
}) => {
  const [editId, setEditId] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [applicantToDelete, setApplicantToDelete] = useState(null);
  const [user] = useAuthState(auth);

  // State for selected visa category
  const [selectedVisa, setSelectedVisa] = useState("");

  // Refs for edit fields
  const nameRef = useRef();
  const emailRef = useRef();

  useEffect(() => {
    let unsubscribe = () => { };

    async function fetchApplicants() {
      if (user) {
        const q = query(collection(db, "applicants"), where("attorney_id", "==", user.uid));

        unsubscribe = onSnapshot(
          q,
          (snapshot) => {
            const newApplicants = snapshot.docs.map((doc) => ({
              id: doc.id,
              ...doc.data(),
            }));
            setApplicants(newApplicants);
          },
          (error) => {
            console.error("Error fetching applicants:", error);
          }
        );
      }
    }

    fetchApplicants();

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
        visaCategory: "", // Add visaCategory field
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
        await setDoc(
          doc(collection(db, "applicants"), applicant.id),
          {
            attorney_id: user.uid,
            name: nameRef.current.value || "",
            email: emailRef.current.value || "",
            visaCategory: selectedVisa || applicant.visaCategory, // Save visaCategory
          },
          { merge: true }
        );
      }
    } catch (error) {
      console.error("Failed to save applicant:", error);
    }
    setEditId(null);
  };

  const deleteApplicant = async (applicant) => {
    try {
      if (selectedApplicant && selectedApplicant.id === applicant.id) {
        setSelectedApplicant(null);
      }
      await deleteDoc(doc(collection(db, "applicants"), applicant.id));
      onClose();
    } catch (error) {
      console.error("Failed to delete applicant:", error);
    }
  };

  const confirmDelete = (applicant) => {
    setApplicantToDelete(applicant);
    onOpen();
  };

  const handleKeyDown = (e, applicant) => {
    if (e.key === "Enter") {
      saveEdit(applicant);
    }
  };

  const handleVisaCategoryChange = async (applicant, newVisaCategory) => {
    try {
      setSelectedVisa(newVisaCategory); // Update the state
      if (applicant) {
        await updateDoc(doc(db, "applicants", applicant.id), { visaCategory: newVisaCategory });
      }
    } catch (error) {
      console.error("Failed to update visa category:", error);
    }
  };

  const handleNavigate = (view, applicant) => {
    setSelectedApplicant(applicant);
    setCurrentView(view);
  };

  // Full Component Code with Adjustments
  return (
    <Box className="oai-manage-view" width="100%">
      <Center className="oai-manage-table-center">
        <Box
          className="oai-manage-table-container"
          overflowX="auto"
          minWidth="60%"
          maxWidth="90%"
          border="1px"
          borderColor="gray.600"
          borderRadius="8px"
        >
          <Box
            p="6"
            // bg="blue.800"
            borderRadius="md"
            boxShadow="lg"
            // border="1px solid"
            borderColor="blue.600"
            color="white"
            mb="6"
            mt="8" /* Add margin-top for spacing before the section */
          >
            <Text fontSize="2xl" fontWeight="bold" mb="4" color="white">
              How to Use Orison
            </Text>
            <Box as="ul" pl="6" fontSize="md" lineHeight="1.8" color="blue.100">
              <Box as="li" mb="2">Use the AI Toolbox to navigate</Box>
              <Box as="li" mb="2">Enter relevant links, upload documents, and provide additional information</Box>
              <Box as="li" mb="2">Choose default questionnaire templates or create custom questions</Box>
              <Box as="li" mb="2">Generate answers for questionnaires using your provided information</Box>
              <Box as="li" mb="2">Generate evidence letters seamlessly</Box>
              <Box as="li">Use DocAssist to chat with your documents and quickly find specific information</Box>
            </Box>
          </Box>
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
              {applicants.map((applicant) => (
                <Tr key={applicant.id}>
                  <Td whiteSpace="nowrap">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.name}
                        ref={nameRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : (
                      applicant.name
                    )}
                  </Td>
                  <Td whiteSpace="nowrap">
                    {editId === applicant.id ? (
                      <Input
                        defaultValue={applicant.email}
                        ref={emailRef}
                        onKeyDown={(e) => handleKeyDown(e, applicant)}
                      />
                    ) : (
                      applicant.email
                    )}
                  </Td>
                  <Td>
                    {editId === applicant.id ? (
                      <Select
                        placeholder="Select Visa Type"
                        value={selectedVisa || applicant.visaCategory || ""}
                        onChange={(e) => {
                          const newVisaCategory = e.target.value;
                          setSelectedVisa(newVisaCategory); // Update the selectedVisa state
                        }}
                      >
                        {visaCategories.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </Select>
                    ) : (
                      applicant.visaCategory || "N/A"
                    )}
                  </Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={Button}
                        rightIcon={<ChevronDownIcon />}
                        isDisabled={!applicant.visaCategory || applicant.visaCategory === "N/A"}
                      >
                        AI Toolbox
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
                        <MenuItem onClick={() => handleNavigate(Views.EVIDENCE, applicant)}>
                          EvidenceLetter
                        </MenuItem>
                        <MenuItem onClick={() => handleNavigate(Views.DOCASSIST, applicant)}>
                          DocAssist
                        </MenuItem>
                      </MenuList>
                    </Menu>
                    {editId === applicant.id ? (
                      <IconButton
                        ml="8px"
                        icon={<CheckIcon />}
                        onClick={() => saveEdit({ ...applicant, visaCategory: selectedVisa })}
                        colorScheme="green"
                      />
                    ) : (
                      <IconButton
                        ml="8px"
                        icon={<EditIcon />}
                        onClick={() => startEdit(applicant.id)}
                        colorScheme="blue"
                      />
                    )}
                    <IconButton
                      ml="8px"
                      icon={<CloseIcon />}
                      onClick={() => confirmDelete(applicant)}
                      colorScheme="red"
                      variant="ghost"
                    />
                  </Td>
                </Tr>

              ))}
            </Tbody>
          </Table>
        </Box>
      </Center >
      <Center className="oai-manage-addnewapp-button-center">
        <Button mt="16px" colorScheme="blue" onClick={addNewApplicant}>
          Add New Applicant
        </Button>
      </Center>
      <DeleteApplicantModal
        isOpen={isOpen}
        onClose={onClose}
        onDelete={() => deleteApplicant(applicantToDelete)}
        applicant={applicantToDelete}
      />
    </Box >
  );
};


export default ManageApplicants;
