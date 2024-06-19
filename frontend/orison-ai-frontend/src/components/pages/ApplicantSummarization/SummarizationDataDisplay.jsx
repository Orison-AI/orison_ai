// ./components/pages/ApplicantSummarization/SummarizationDataDisplay.jsx

// React
import React from 'react';

// Chakra UI
import { Box, Text } from '@chakra-ui/react';

// Orison AI
import StructuredData from '../../StructuredData';

const SummarizationDataDisplay = ({ data }) => {
  const keys = [
    { key: "summary", collapsible: true, dynamic: true, dynamic_collapsible: true, subKeys: [
        { key: "answer" },
        { key: "question" },
        { key: "source" },
      ]
    }
  ];

  return (
    <Box bg="gray.900" p="20px" overflowY="auto" borderRadius="20px" width="60%" maxHeight="60%" minWidth="600px">
      <Text fontSize="2xl" mb="4">Summary</Text>
      <StructuredData data={data} keys={keys} />
    </Box>
  );
};

export default SummarizationDataDisplay;
