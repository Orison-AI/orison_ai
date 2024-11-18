// React
import React, { useState, useEffect } from "react";

// Chakra
import { Box, Button, VStack, HStack, useToast, Spacer } from "@chakra-ui/react";

// Internal
import QuestionEditor from "./QuestionEditor";
import {
  fetchQuestionnaire,
  fetchTags,
  handleTagChange,
  updateQuestion,
  editQuestion,
  deleteQuestion,
  addQuestion,
  createFromTemplate,
  deleteAllQuestions,
} from "./questionnaireUtils";
import { useApplicantContext } from "../../../context/ApplicantContext";

const QuestionnaireEditor = ({ }) => {
  const [questions, setQuestions] = useState([]);
  const [idCounter, setIdCounter] = useState(0);
  const [allTags, setAllTags] = useState([]);
  const [documentExists, setDocumentExists] = useState(false);
  const toast = useToast();
  const [isAdding, setIsAdding] = useState(false);
  const { selectedApplicant } = useApplicantContext();

  // Fetch tags and questionnaire data
  useEffect(() => {
    if (!selectedApplicant?.id) {
      console.error("No applicant ID provided.");
      return;
    }

    (async () => {
      try {
        const tags = await fetchTags(selectedApplicant);
        setAllTags(tags);

        const { questions: fetchedQuestions, exists } = await fetchQuestionnaire(
          selectedApplicant.id
        );
        setQuestions(fetchedQuestions);
        setIdCounter(fetchedQuestions.length);
        setDocumentExists(exists);
      } catch (error) {
        console.error("Error loading data:", error);
        toast({
          title: "Error",
          description: "Could not load questionnaire data.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
    })();
  }, [selectedApplicant, toast]);

  // Handle delete all questions
  const handleDeleteAll = async () => {
    try {
      if (!selectedApplicant?.id) throw new Error("No applicant ID provided.");
      // Clear Firestore task array
      await deleteAllQuestions(selectedApplicant.id);

      // Clear UI state
      setQuestions([]);
      setIdCounter(0);
      setIsAdding(false); // Ensure adding state is reset
      toast({
        title: "All Questions Deleted",
        description: "All questions have been removed from the questionnaire.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error deleting all questions:", error);
      toast({
        title: "Error",
        description: "Failed to delete all questions.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };


  return (
    <Box className="oai-questionnaire-editor" width="100%">
      {/* Buttons */}
      <HStack spacing={4} mb={4}>
        <Button
          onClick={() =>
            createFromTemplate(selectedApplicant, setQuestions, setDocumentExists)
          }
          colorScheme="blue" // Changed color scheme
        >
          Add from Template
        </Button>

        <Button onClick={handleDeleteAll} colorScheme="orange">
          Delete All Questions
        </Button>
      </HStack>

      {/* Render Questions */}
      <VStack spacing={4} align="stretch">
        {questions.map((question) => (
          <QuestionEditor
            key={question.id}
            question={question}
            allTags={allTags}
            onTagChange={(updatedTags) =>
              handleTagChange(
                selectedApplicant.id,
                question.id,
                updatedTags,
                questions,
                setQuestions
              )
            }
            onSave={(id, text, tag, detail_level) =>
              updateQuestion(
                selectedApplicant.id,
                id,
                text,
                tag,
                detail_level,
                questions,
                setQuestions
              )
            }
            onEdit={() => editQuestion(question.id, questions, setQuestions)}
            onDelete={() =>
              deleteQuestion(selectedApplicant.id, question.id, questions, setQuestions)
            }
          />
        ))}
        {/* Add a New Question */}
        {!isAdding ? (
          <Button
            onClick={() => {
              addQuestion(setIdCounter, questions, setQuestions);
              setIsAdding(true); // Enter adding mode
            }}
            colorScheme="green"
          >
            +
          </Button>
        ) : (
          <HStack spacing={4}>
            <Button
              onClick={() => {
                // Remove the last added question and exit adding mode
                const updatedQuestions = [...questions];
                updatedQuestions.pop(); // Remove the last added question
                setQuestions(updatedQuestions);
                setIsAdding(false); // Exit adding mode
              }}
              colorScheme="gray"
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                setIsAdding(false); // Exit adding mode after saving
              }}
              colorScheme="blue"
            >
              Save
            </Button>
          </HStack>
        )}
      </VStack>
    </Box>
  );
};

export default QuestionnaireEditor;
