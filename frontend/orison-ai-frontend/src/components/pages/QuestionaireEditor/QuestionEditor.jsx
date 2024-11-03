// ./components/pages/QuestionaireEditor/QuestionEditor.jsx

import React, { useState, useEffect } from 'react';
import { Input, Button, HStack, Spacer, Select } from '@chakra-ui/react';

const DETAIL_LEVELS = [
  { label: "Light Detail", value: "light detail" },
  { label: "Moderate Detail", value: "moderate detail" },
  { label: "Lengthy Detail", value: "lengthy detail" },
  { label: "Very Heavy Detail", value: "very heavy detail" },
];

const QuestionEditor = ({ question, onSave, onEdit, onDelete, tags }) => {
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
          <Select
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Select tag"
          >
            {tags.map((tagOption) => (
              <option key={tagOption.value} value={tagOption.value}>
                {tagOption.label}
              </option>
            ))}
          </Select>
          <Select
            value={detailLevel}
            onChange={(e) => setDetailLevel(e.target.value)}
            placeholder="Select detail level"
          >
            {DETAIL_LEVELS.map((level) => (
              <option key={level.value} value={level.value}>
                {level.label}
              </option>
            ))}
          </Select>
          <Spacer />
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
          <Spacer />
          <Button onClick={onEdit} colorScheme="yellow">Edit</Button>
          <Button onClick={onDelete} colorScheme="red">Delete</Button>
        </>
      )}
    </HStack>
  );
};

export default QuestionEditor;
