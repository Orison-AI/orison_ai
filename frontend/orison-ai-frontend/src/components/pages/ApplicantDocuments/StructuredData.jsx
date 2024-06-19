// ./components/pages/Documents/StructuredData.jsx

// React
import React from 'react';

// Chakra UI
import { Box, Text, VStack } from '@chakra-ui/react';

const StructuredData = ({ data }) => {
  const renderData = (data, level = 0) => {
    if (typeof data !== 'object' || data === null) {
      return <Text ml={`${level * 20}px`}>{data}</Text>;
    }
    return Object.keys(data).map(key => (
      <Box key={key} ml={`${level * 20}px`}>
        <Text fontWeight="bold">{key}:</Text>
        <Box ml="20px">
          {renderData(data[key], level + 1)}
        </Box>
      </Box>
    ));
  };

  return (
    <VStack align="start">
      {renderData(data)}
    </VStack>
  );
};

export default StructuredData;
