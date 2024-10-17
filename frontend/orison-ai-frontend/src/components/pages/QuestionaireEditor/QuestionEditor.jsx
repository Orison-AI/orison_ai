// ./components/pages/QuestionaireEditor/QuestionEditor.jsx

import React, { useState } from 'react';
import { Input, Button, HStack, Spacer } from '@chakra-ui/react';

const QuestionEditor = ({ question, onSave, onEdit, onDelete }) => {
  const [text, setText] = useState(question.text);  // Initialize text state
  const [tag, setTag] = useState(question.tag);  // Initialize tag state
  const [detailLevel, setDetailLevel] = useState(question.detail_level);  // Initialize detail_level state

  return (
    <HStack width="100%" spacing={4}>
      {question.isEditing ? (
        <>
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Edit question"
          />
          <Input
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Edit tag"
          />
          <Input
            value={detailLevel}
            onChange={(e) => setDetailLevel(e.target.value)}
            placeholder="Edit detail level"
          />
          <Spacer />  {/* This pushes buttons to the right */}
          <Button
            onClick={() => onSave(question.id, text, tag, detailLevel)}  // Pass all values on save
            colorScheme="green"
          >
            Save
          </Button>
        </>
      ) : (
        <>
          <div>{text} (Tag: {tag}, Detail Level: {detailLevel})</div>
          <Spacer />  {/* This pushes buttons to the right */}
          <Button onClick={onEdit} colorScheme="yellow">Edit</Button>
          <Button onClick={onDelete} colorScheme="red">Delete</Button>
        </>
      )}
    </HStack>
  );
};

export default QuestionEditor;
