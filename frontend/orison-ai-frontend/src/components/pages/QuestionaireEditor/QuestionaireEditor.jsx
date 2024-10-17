// ./components/pages/QuestionaireEditor/QuestionaireEditor.jsx

// React
import React, { useState } from 'react';

// Chakra
import { Box, Button, VStack } from '@chakra-ui/react';

// Internal
import QuestionEditor from './QuestionEditor';

const QuestionaireEditor = () => {
  const [questions, setQuestions] = useState([]);

  const addQuestion = () => {
    setQuestions([...questions, { id: Date.now(), text: '', isEditing: true }]);
  };

  const updateQuestion = (id, text) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, text, isEditing: false } : q));
  };

  const editQuestion = (id) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, isEditing: true } : q));
  };

  const deleteQuestion = (id) => {
    setQuestions(questions.filter(q => q.id !== id));
  };

  return (
    <Box className="oai-questionaire-editor" width="100%">
      <VStack spacing={4}>
        {questions.map(question => (
          <QuestionEditor
            key={question.id}
            question={question}
            onSave={updateQuestion}
            onEdit={editQuestion}
            onDelete={deleteQuestion}
          />
        ))}
        <Button onClick={addQuestion} colorScheme="blue">+</Button>
      </VStack>
    </Box>
  );
};

export default QuestionaireEditor;
