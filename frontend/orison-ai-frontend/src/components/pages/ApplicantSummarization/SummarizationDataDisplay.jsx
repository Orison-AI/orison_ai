// ./components/pages/ApplicantSummarization/SummarizationDataDisplay.jsx

// React
import React from 'react';

// Chakra UI
import { Box, Text, VStack, Heading } from '@chakra-ui/react';

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

  return (
    <Box bg="gray.900" p="40px" borderRadius="10px" width="100%">
      <Heading size="md" mb={4}>Question</Heading>
      <Text mb={4}>{question}</Text>

      <Heading size="md" mb={4}>Answer</Heading>
      <Box mb={4}>
        <ReactMarkdown>{answer}</ReactMarkdown>
      </Box>

      <Heading size="md" mb={4}>Sources</Heading>
      <Text>{source}</Text>
    </Box>
  );
};

export default SummarizationDataDisplay;
