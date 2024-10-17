// ./components/pages/QuestionaireEditor/QuestionaireEditor.jsx

// React
import React, { useState, useEffect } from 'react';

// Firebase
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { auth, db } from '../../../common/firebaseConfig';  // Assuming you have auth and db setup

// Chakra
import { Box, Button, VStack } from '@chakra-ui/react';

// Internal
import QuestionEditor from './QuestionEditor';

const QuestionaireEditor = () => {
  const [questions, setQuestions] = useState([]);
  const [idCounter, setIdCounter] = useState(0); // Initialize ID counter

  // Fetch the questionnaire for the attorney when the component mounts
  useEffect(() => {
    const fetchQuestionnaire = async () => {
      try {
        const user = auth.currentUser;
        if (!user) {
          throw new Error('User not authenticated');
        }

        // Reference to the specific attorney's questionnaire document
        const questionnaireDocRef = doc(db, 'templates', 'attorneys', user.uid, 'eb1_a_questionnaire');
        const questionnaireDoc = await getDoc(questionnaireDocRef);

        if (questionnaireDoc.exists()) {
          const questionnaireData = questionnaireDoc.data();

          // Extract the 'task' array which contains question, tag, and detail_level
          const taskArray = questionnaireData.task || [];

          // Map the tasks to extract all fields: question, tag, detail_level, and assign unique IDs
          const extractedQuestions = taskArray.map((taskItem, index) => ({
            id: index + 1,  // Assign unique ID using index + 1
            text: taskItem.question,  // The question text
            tag: taskItem.tag || '',  // Tag field
            detail_level: taskItem.detail_level || '',  // Detail level field
            isEditing: false  // Default to not editing
          }));

          // Update the state with the extracted questions and set ID counter
          setQuestions(extractedQuestions);
          setIdCounter(extractedQuestions.length);  // Initialize ID counter based on the number of questions
        } else {
          console.error('Questionnaire document not found!');
        }
      } catch (error) {
        console.error('Error fetching questionnaire:', error);
      }
    };

    // Call the fetch function when component mounts
    fetchQuestionnaire();
  }, []);  // Empty dependency array ensures it only runs once on mount

  // Function to update Firestore after any change (add, edit, delete)
  const updateFirestore = async (updatedQuestions) => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('User not authenticated');

      // Update the Firestore document with the new questions array
      const questionnaireDocRef = doc(db, 'templates', 'attorneys', user.uid, 'eb1_a_questionnaire');
      const updatedTaskArray = updatedQuestions.map(q => ({
        question: q.text,
        tag: q.tag,
        detail_level: q.detail_level
      }));

      // Update Firestore with the new task array
      await updateDoc(questionnaireDocRef, { task: updatedTaskArray });

      console.log('Firestore updated with new questions');
    } catch (error) {
      console.error('Error updating Firestore:', error);
    }
  };

  // Add a new question and update Firestore
  const addQuestion = () => {
    const newQuestion = {
      id: idCounter + 1,  // Increment the ID counter
      text: '',
      tag: 'research',  // Default tag
      detail_level: 'light',  // Default detail level
      isEditing: true
    };

    const updatedQuestions = [...questions, newQuestion];
    setQuestions(updatedQuestions);
    setIdCounter(idCounter + 1);  // Increment the ID counter for future additions

    // Update Firestore with the new question added
    updateFirestore(updatedQuestions);
  };

  // Update a question's text, tag, and detail_level, then update Firestore
  const updateQuestion = (id, text, tag, detail_level) => {
    const updatedQuestions = questions.map(q =>
      q.id === id ? { ...q, text, tag, detail_level, isEditing: false } : q
    );
    setQuestions(updatedQuestions);

    // Update Firestore with the edited question
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

    // Update Firestore with the question deleted
    updateFirestore(updatedQuestions);
  };

  return (
    <Box className="oai-questionaire-editor" width="100%">
      <VStack spacing={4}>
        {questions.map(question => (
          <QuestionEditor
            key={question.id}  // Use ID as the key
            question={question}
            onSave={(id, text, tag, detail_level) => updateQuestion(id, text, tag, detail_level)}  // Pass ID and fields on save
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
