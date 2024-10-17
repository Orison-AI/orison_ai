// ./components/pages/QuestionaireEditor/Question.jsx

// React
import React, { useState, useRef } from 'react';

// Chakra
import { Box, Input, IconButton, HStack } from '@chakra-ui/react';
import { EditIcon, CloseIcon, CheckIcon } from '@chakra-ui/icons';

const Question = ({ question, onSave, onEdit, onDelete }) => {
  const [text, setText] = useState(question.text);
  const inputRef = useRef();

  const handleSave = () => {
    onSave(question.id, text);
  };

  const handleEdit = () => {
    onEdit(question.id);
  };

  const handleDelete = () => {
    onDelete(question.id);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSave();
    }
  };

  return (
    <HStack spacing={2} width="100%">
      {question.isEditing ? (
        <Input
          ref={inputRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      ) : (
        <Box flex="1">{question.text}</Box>
      )}
      {question.isEditing ? (
        <IconButton icon={<CheckIcon />} onClick={handleSave} colorScheme="green" />
      ) : (
        <IconButton icon={<EditIcon />} onClick={handleEdit} colorScheme="blue" />
      )}
      <IconButton icon={<CloseIcon />} onClick={handleDelete} colorScheme="red" />
    </HStack>
  );
};

export default Question;
