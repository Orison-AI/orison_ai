// ./components/pages/Documents/StructuredData.jsx

// React
import React from 'react';

// Chakra UI
import { Box, Text, VStack } from '@chakra-ui/react';

const StructuredData = ({ data, keys }) => {
  const renderData = (data, keys, level = 0) => {
    if (typeof data !== 'object' || data === null) {
      return <Text ml={`${level * 10}px`}>{data}</Text>;
    }

    return keys.map(keyInfo => {
      const key = typeof keyInfo === 'string' ? keyInfo : keyInfo.key;
      const subKeys = typeof keyInfo === 'object' && keyInfo.subKeys ? keyInfo.subKeys : null;

      if (!(key in data)) {
        return null;
      }

      return (
        <Box key={key} ml={`${level * 10}px`}>
          <Text fontWeight="bold" display="inline">{key}:</Text>
          {typeof data[key] === 'object' && subKeys ? (
            <Box ml="10px">
              {renderData(data[key], subKeys, level + 1)}
            </Box>
          ) : (
            <Text display="inline" ml="10px">{data[key]}</Text>
          )}
        </Box>
      );
    });
  };

  return (
    <VStack align="start">
      {renderData(data, keys)}
    </VStack>
  );
};

export default StructuredData;
