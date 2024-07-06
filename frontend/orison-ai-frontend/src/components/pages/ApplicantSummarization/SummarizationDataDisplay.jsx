// ./components/pages/ApplicantSummarization/SummarizationDataDisplay.jsx

// React
import React, { useState } from 'react';

// Chakra UI
import { Box, Text, VStack, Heading, Collapse, Button, HStack } from '@chakra-ui/react';

// React Markdown
import ReactMarkdown from 'react-markdown';

const SummarizationDataDisplay = ({ data }) => {
  const summaries = data.summary || [];

  return (
    <VStack spacing={4} width="100%">
      {summaries.map((item, index) => (
        <SummaryCard key={index} item={item} />
      ))}
    </VStack>
  );
};

// Individual card for each summary item
const SummaryCard = ({ item }) => {
  const { question, answer, source } = item;
  const [isOpen, setIsOpen] = useState(false);

  const toggleCollapse = () => setIsOpen(!isOpen);

  return (
    <Box bg="gray.900" p="20px" borderRadius="10px" width="100%">
      <HStack spacing={4} align="start">
      <Button
        onClick={toggleCollapse}
        size="lg"
        variant="link"
        fontSize="2xl"
        padding="0"
        height="auto"
        sx={{
          textDecoration: 'none',
          _hover: { textDecoration: 'none', color: 'blue.500' }, // Remove underline and change color on hover
        }}
      >
        {isOpen ? '▼' : '▶'}
      </Button>
        <Box>
          <Heading size="md" mb={4}>Question</Heading>
          <Text mb={4}>{question}</Text>

          <Collapse in={isOpen} animateOpacity>
            <Box>
              <Heading size="md" mb={4}>Answer</Heading>
              <Box mb={4}>
                <ReactMarkdown>{answer}</ReactMarkdown>
              </Box>

              <Heading size="md" mb={4}>Sources</Heading>
              <Text mb={4}>{source}</Text>
            </Box>
          </Collapse>
        </Box>
      </HStack>
    </Box>
  );
};

export default SummarizationDataDisplay;
