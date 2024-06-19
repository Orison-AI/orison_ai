// ./components/StructuredData.jsx

// React
import React, { useState } from 'react';

// Chakra UI
import { Box, Text, VStack, Collapse, Button } from '@chakra-ui/react';

const StructuredData = ({ data, keys }) => {
  const [collapsedKeys, setCollapsedKeys] = useState({});

  const toggleCollapse = key => {
    setCollapsedKeys(prevState => ({
      ...prevState,
      [key]: !prevState[key]
    }));
  };

  const renderData = (data, keys, level = 0) => {
    if (!Array.isArray(keys)) {
      return null; // Ensure keys is an array
    }

    if (typeof data !== 'object' || data === null) {
      return <Text ml={`${level * 10}px`}>{data}</Text>;
    }

    return keys.map(keyInfo => {
      const key = typeof keyInfo === 'string' ? keyInfo : keyInfo.key;
      const subKeys = typeof keyInfo === 'object' && keyInfo.subKeys ? keyInfo.subKeys : null;
      const dynamic = typeof keyInfo === 'object' && keyInfo.dynamic ? keyInfo.dynamic : false;
      const collapsible = typeof keyInfo === 'object' && keyInfo.collapsible ? keyInfo.collapsible : false;
      const dynamicCollapsible = typeof keyInfo === 'object' && keyInfo.dynamic_collapsible ? keyInfo.dynamic_collapsible : false;

      if (!(key in data)) {
        return null;
      }

      const isCollapsed = collapsible && collapsedKeys[key];

      return (
        <Box key={key} ml={`${level * 10}px`}>
          {collapsible ? (
            <Button onClick={() => toggleCollapse(key)} size="s" variant="link" fontWeight="bold">
              {isCollapsed ? '▶' : '▼'} {key}
            </Button>
          ) : (
            <Text fontWeight="bold" display="inline">{key}:</Text>
          )}
          {dynamic ? (
            <Collapse in={!isCollapsed}>
              <Box ml="10px">
                {Object.keys(data[key]).map(dynamicKey => (
                  <Box key={dynamicKey} ml="10px">
                    {dynamicCollapsible ? (
                      <Button onClick={() => toggleCollapse(`${key}-${dynamicKey}`)} size="xs" variant="link" fontWeight="bold">
                        {collapsedKeys[`${key}-${dynamicKey}`] ? '▶' : '▼'} {dynamicKey}
                      </Button>
                    ) : (
                      <Text fontWeight="bold" display="inline">{dynamicKey}:</Text>
                    )}
                    
                    {typeof data[key][dynamicKey] === 'object' && subKeys ? (
                      <Collapse in={!collapsedKeys[`${key}-${dynamicKey}`]}>
                        <Box ml="10px">
                          {renderData(data[key][dynamicKey], subKeys, level + 1)}
                        </Box>
                      </Collapse>
                    ) : (
                      <Text display="inline" ml="10px">{data[key][dynamicKey]}</Text>
                    )}
                  </Box>
                ))}
              </Box>
            </Collapse>
          ) : typeof data[key] === 'object' && subKeys ? (
            <Collapse in={!isCollapsed}>
              <Box ml="10px">
                {renderData(data[key], subKeys, level + 1)}
              </Box>
            </Collapse>
          ) : (
            <Text display="inline" ml="10px">{data[key]}</Text>
          )}
        </Box>
      );
    });
  };

  return (
    <VStack align="start" fontFamily="monospace">
      {renderData(data, keys)}
    </VStack>
  );
};

export default StructuredData;
