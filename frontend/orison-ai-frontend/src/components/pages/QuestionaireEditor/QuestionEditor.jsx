import React, { useState } from "react";
import {
  Input,
  Button,
  HStack,
  VStack,
  Select,
  Tag,
  TagLabel,
  TagCloseButton,
  Spacer,
  Text,
  Box,
} from "@chakra-ui/react";

const DETAIL_LEVELS = [
  { label: "Light", value: "light" },
  { label: "Moderate", value: "moderate" },
  { label: "Lengthy", value: "lengthy" },
  { label: "Heavy", value: "heavy" },
];

const QuestionEditor = ({ question, onSave, onEdit, onDelete, allTags }) => {
  const [text, setText] = useState(question.text);
  const [selectedTags, setSelectedTags] = useState(question.tag || []);
  const [detailLevel, setDetailLevel] = useState(question.detail_level);

  // Handle adding a new tag
  const handleAddTag = (e) => {
    const tag = e.target.value;
    if (tag && !selectedTags.includes(tag)) {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  // Handle removing a tag
  const handleRemoveTag = (tagToRemove) => {
    setSelectedTags(selectedTags.filter((tag) => tag !== tagToRemove));
  };

  return (
    <Box
      width="100%"
      p={4}
      border="1px solid"
      borderColor="gray.200"
      borderRadius="md"
      shadow="sm"
    >
      {question.isEditing ? (
        <VStack spacing={4} align="stretch">
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Edit question"
          />
          <VStack align="stretch">
            <Text fontWeight="bold">Tags:</Text>
            <HStack spacing={2} wrap="wrap">
              {selectedTags.map((tag) => (
                <Tag
                  key={tag}
                  size="md"
                  borderRadius="full"
                  variant="solid"
                  colorScheme="blue"
                >
                  <TagLabel>{tag}</TagLabel>
                  <TagCloseButton onClick={() => handleRemoveTag(tag)} />
                </Tag>
              ))}
            </HStack>
            <Select placeholder="Add a tag" onChange={handleAddTag}>
              {allTags.map((tagOption) => (
                <option key={tagOption} value={tagOption}>
                  {tagOption}
                </option>
              ))}
            </Select>
          </VStack>
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
          <HStack justifyContent="flex-end" width="100%">
            <Button
              onClick={() =>
                onSave(question.id, text, selectedTags, detailLevel)
              }
              colorScheme="green"
            >
              Save
            </Button>
          </HStack>
        </VStack>
      ) : (
        <VStack spacing={2} align="stretch">
          <Text fontWeight="bold">{text}</Text>
          <HStack alignItems="center">
            <VStack align="start" spacing={1}>
              <HStack spacing={2} wrap="wrap">
                <Text fontSize="sm" color="gray.500">
                  <strong>Tags:</strong>
                </Text>
                {selectedTags.length > 0 ? (
                  selectedTags.map((tag) => (
                    <Tag
                      key={tag}
                      size="md"
                      borderRadius="full"
                      variant="solid"
                      colorScheme="blue"
                    >
                      {tag}
                    </Tag>
                  ))
                ) : (
                  <Text fontSize="sm" color="gray.500">
                    None
                  </Text>
                )}
              </HStack>
              {/* <Text fontSize="sm" color="gray.500">
                <strong>Detail Level:</strong> {detailLevel || "N/A"}
              </Text> */}
            </VStack>
            <Spacer />
            <HStack spacing={2}>
              <Button onClick={onEdit} colorScheme="yellow" size="sm">
                Edit
              </Button>
              <Button onClick={onDelete} colorScheme="red" size="sm">
                Delete
              </Button>
            </HStack>
          </HStack>
        </VStack>
      )}
    </Box>
  );
};

export default QuestionEditor;
