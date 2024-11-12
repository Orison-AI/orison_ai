// React
import React, { useState, useEffect, useCallback } from 'react';

// Firebase
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';
import { auth, db } from '../../../common/firebaseConfig'; // Assuming you have auth and db setup

// Chakra
import { Box, Button, VStack, useToast } from '@chakra-ui/react';

// Internal
import QuestionEditor from './QuestionEditor';

const QuestionaireEditor = ({ selectedApplicant }) => {
  const [questions, setQuestions] = useState([]);
  const [idCounter, setIdCounter] = useState(0); // Initialize ID counter
  const [documentExists, setDocumentExists] = useState(false);
  const toast = useToast();
  const [tags, setTags] = useState([]); // Store fetched tags here
  const [detail_levels, setDetailLevel] = useState([]); // Store fetched detail levels here

  // Fetch the questionnaire for the attorney when the component mounts
  useEffect(() => {
    const fetchQuestionnaire = async () => {
      try {
        const user = auth.currentUser;
        if (!user) throw new Error('User not authenticated');

        // Reference to the specific attorney's questionnaire document
        const questionnaireDocRef = doc(db, 'templates', selectedApplicant.id);
        const questionnaireDoc = await getDoc(questionnaireDocRef);

        if (questionnaireDoc.exists()) {
          setDocumentExists(true);  // Document exists
          const questionnaireData = questionnaireDoc.data();

          // Extract the 'task' array which contains question, tag, and detail_level
          const taskArray = questionnaireData.task || [];

          // Map the tasks to extract all fields: question, tag, detail_level, and assign unique IDs
          const extractedQuestions = taskArray.map((taskItem, index) => ({
            id: index + 1,
            text: taskItem.question,
            tag: taskItem.tag || '',
            detail_level: taskItem.detail_level || '',
            isEditing: false
          }));

          setQuestions(extractedQuestions);
          setIdCounter(extractedQuestions.length);
        } else {
          setDocumentExists(false);  // Document doesn't exist
        }
      } catch (error) {
        console.error('Error fetching questionnaire:', error);
      }
    };

    fetchQuestionnaire();
  }, []);

  // Function to create the questionnaire from a template
  const createFromTemplate = async () => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('User not authenticated');

      // Get the default questionnaire template
      const templateDocRef = doc(db, 'templates', 'eb1_a_questionnaire');
      const templateDoc = await getDoc(templateDocRef);

      if (templateDoc.exists()) {
        const templateData = templateDoc.data();
        const templateTasks = templateData.task || [];

        // Reference to the user's questionnaire document
        const questionnaireDocRef = doc(db, 'templates', selectedApplicant.id);
        const userDocSnapshot = await getDoc(questionnaireDocRef);

        let updatedTaskArray;

        if (userDocSnapshot.exists()) {
          // If the document exists, append new questions to the existing task array
          const existingData = userDocSnapshot.data();
          const existingTasks = existingData.task || [];

          // Combine existing tasks with template tasks
          updatedTaskArray = [...existingTasks, ...templateTasks];
        } else {
          // If the document does not exist, use the template tasks directly
          updatedTaskArray = templateTasks;
        }

        // Update Firestore with the combined task array
        await setDoc(questionnaireDocRef, { task: updatedTaskArray }, { merge: true });

        // Update local state with the combined questions for display
        const extractedQuestions = updatedTaskArray.map((taskItem, index) => ({
          id: index + 1,
          text: taskItem.question,
          tag: taskItem.tag || '',
          detail_level: taskItem.detail_level || '',
          isEditing: false
        }));

        setQuestions(extractedQuestions);
        setIdCounter(extractedQuestions.length);
        setDocumentExists(true);

        toast({
          title: "Questionnaire Updated",
          description: "The default template has been appended to your existing questionnaire.",
          status: "info",
          duration: 5000,
          isClosable: true,
        });
      } else {
        console.error("Default questionnaire template not found.");
      }
    } catch (error) {
      console.error("Error creating questionnaire from template:", error);
      toast({
        title: "Error",
        description: `Error creating the questionnaire: ${error.message}`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };


  // Function to update Firestore after any change
  const updateFirestore = async (updatedQuestions) => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('User not authenticated');

      const questionnaireDocRef = doc(db, 'templates', selectedApplicant.id);
      const updatedTaskArray = updatedQuestions.map(q => ({
        question: q.text,
        tag: q.tag,
        detail_level: q.detail_level
      }));

      // First, check if the document exists
      const docSnapshot = await getDoc(questionnaireDocRef);

      if (docSnapshot.exists()) {
        // If document exists, update it
        await updateDoc(questionnaireDocRef, { task: updatedTaskArray });
        console.log('Firestore updated with new questions');
      } else {
        // If document does not exist, create it
        await setDoc(questionnaireDocRef, { task: updatedTaskArray });
        console.log('Firestore document created with new questions');
      }
    } catch (error) {
      console.error('Error updating Firestore:', error);
    }
  };


  // Add a new question and update Firestore
  const addQuestion = () => {
    const newQuestion = {
      id: idCounter + 1,
      text: '',
      tag: 'research',
      detail_level: 'light',
      isEditing: true
    };

    const updatedQuestions = [...questions, newQuestion];
    setQuestions(updatedQuestions);
    setIdCounter(idCounter + 1);
    updateFirestore(updatedQuestions);
  };

  // Update a question's text, tag, and detail_level
  const updateQuestion = (id, text, tag, detail_level) => {
    const updatedQuestions = questions.map(q =>
      q.id === id ? { ...q, text, tag, detail_level, isEditing: false } : q
    );
    setQuestions(updatedQuestions);
    updateFirestore(updatedQuestions);
  };

  // Edit a question
  const editQuestion = (id) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, isEditing: true } : q));
  };

  // Delete a question and update Firestore
  const deleteQuestion = (id) => {
    const updatedQuestions = questions.filter(q => q.id !== id);
    setQuestions(updatedQuestions);
    updateFirestore(updatedQuestions);
  };

  // Fetch tags from Firestore
  const fetchTags = useCallback(async () => {
    try {
      const user = auth.currentUser;
      if (!user || !selectedApplicant) throw new Error("User or applicant not found");

      const docRef = doc(db, "applicants", selectedApplicant.id);
      const docSnap = await getDoc(docRef);

      if (docSnap.exists()) {
        const customTags = docSnap.data().customTags || [];
        const mappedTags = customTags.map(tag => ({
          label: tag,
          value: tag.toLowerCase()
        }));
        const customDetailLevel = docSnap.data().customDetailLevel || [];
        const mappedDetailLevel = customDetailLevel.map(detail_level => ({
          label: detail_level,
          value: detail_level.toLowerCase()
        }));
        setTags(mappedTags);
        setDetailLevel(mappedDetailLevel);
      } else {
        console.error("No document found for the selected applicant.");
      }
    } catch (error) {
      console.error("Error fetching tags:", error);
    }
  }, [selectedApplicant]);

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  // Fetch the questionnaire when the component mounts
  useEffect(() => {
    const fetchQuestionnaire = async () => {
      try {
        const user = auth.currentUser;
        if (!user) throw new Error('User not authenticated');

        const questionnaireDocRef = doc(db, 'templates', selectedApplicant.id);
        const questionnaireDoc = await getDoc(questionnaireDocRef);

        if (questionnaireDoc.exists()) {
          setDocumentExists(true);
          const questionnaireData = questionnaireDoc.data();
          const taskArray = questionnaireData.task || [];

          const extractedQuestions = taskArray.map((taskItem, index) => ({
            id: index + 1,
            text: taskItem.question,
            tag: taskItem.tag || '',
            detail_level: taskItem.detail_level || '',
            isEditing: false
          }));

          setQuestions(extractedQuestions);
          setIdCounter(extractedQuestions.length);
        } else {
          setDocumentExists(false);
        }
      } catch (error) {
        console.error('Error fetching questionnaire:', error);
      }
    };

    fetchQuestionnaire();
  }, []);

  return (
    <Box className="oai-questionnaire-editor" width="100%">
      <Button onClick={createFromTemplate} colorScheme="teal" mb={4}>
        Add from Template
      </Button>

      <VStack spacing={4}>
        {questions.map((question) => (
          <QuestionEditor
            key={question.id}
            question={question}
            tags={tags}  // Pass tags to QuestionEditor
            detailLevels={detail_levels}  // Pass detail_levels to QuestionEditor
            onSave={(id, text, tag, detail_level) => updateQuestion(id, text, tag, detail_level)}
            onEdit={() => editQuestion(question.id)}
            onDelete={() => deleteQuestion(question.id)}
          />
        ))}

        <Button onClick={addQuestion} colorScheme="blue">+</Button>
      </VStack>
    </Box>
  );
};

export default QuestionaireEditor;
