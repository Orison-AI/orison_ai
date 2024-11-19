// React
import React from 'react';

// Chakra UI
import {
  Badge, Box, Button, IconButton, Spinner,
  Table, Thead, Tbody, Tr, Th, Td, HStack,
} from '@chakra-ui/react';
import { CheckCircleIcon, CloseIcon, WarningIcon } from '@chakra-ui/icons';

const FileTable = ({
  documents,
  vectorizeFile,
  unvectorizeFile,
  vectorizeAllFiles,
  unvectorizeAllFiles,
  deleteFile,
  deleteAllFiles, // Add deleteAllFiles prop
  viewFile,
  vectorizingFiles,
  vectorizeStatus,
}) => {
  return (
    <Box
      mb="10px"
      width="100%"
      border="1px"
      borderColor="gray.600"
      borderRadius="10px"
    >
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>File Name</Th>
            <Th>Status</Th>
            <Th>
              <HStack spacing={4} justifyContent="flex-end">
                <Button
                  colorScheme="blue"
                  onClick={vectorizeAllFiles}
                  isDisabled={documents.every(doc => doc.vectorized)}
                >
                  Vectorize All
                </Button>
                <Button
                  colorScheme="red"
                  onClick={unvectorizeAllFiles}
                >
                  Unvectorize All
                </Button>
                <Button
                  colorScheme="red"
                  onClick={async () => {
                    if (
                      window.confirm(
                        'Are you sure you want to delete all files? This action cannot be undone.'
                      )
                    ) {
                      await deleteAllFiles(); // Call deleteAllFiles when clicked
                    }
                  }}
                  isDisabled={documents.length === 0} // Disable if no files
                >
                  Delete All Files
                </Button>
              </HStack>
            </Th>
          </Tr>
        </Thead>
        <Tbody fontSize="16px">
          {documents.map(({ fileName, vectorized }) => {
            const isVectorizing = vectorizingFiles.includes(fileName);

            return (
              <Tr key={fileName}>
                <Td whiteSpace="wrap">{fileName}</Td>
                <Td whiteSpace="nowrap">
                  {vectorized ? (
                    <Badge colorScheme="green">Vectorized</Badge>
                  ) : (
                    <Badge colorScheme="orange">Not Vectorized</Badge>
                  )}
                </Td>
                <Td isNumeric whiteSpace="nowrap">
                  {isVectorizing && vectorizeStatus === 'loading' && <Spinner color="blue.500" size="sm" />}
                  {isVectorizing && vectorizeStatus === 'success' && <CheckCircleIcon color="green.500" />}
                  {isVectorizing && vectorizeStatus === 'error' && <WarningIcon color="red.500" />}

                  <Button
                    ml="16px"
                    colorScheme="blue"
                    onClick={() => vectorizeFile(fileName)}
                    isDisabled={isVectorizing || vectorized}
                  >
                    Vectorize
                  </Button>
                  <Button
                    ml="16px"
                    colorScheme="red"
                    onClick={() => unvectorizeFile(fileName)}
                    isDisabled={!vectorized} // Disable if not vectorized
                    visibility={!vectorized ? 'hidden' : 'visible'} // Optional: hide button completely if not vectorized
                  >
                    Unvectorize
                  </Button>
                  <Button
                    ml="16px"
                    onClick={() => viewFile(fileName)}
                    isDisabled={isVectorizing}
                  >
                    View
                  </Button>
                  <IconButton
                    icon={<CloseIcon />}
                    ml="16px"
                    colorScheme="red"
                    variant="ghost"
                    onClick={() => deleteFile(fileName)}
                    isDisabled={isVectorizing}
                  />
                </Td>
              </Tr>
            );
          })}
        </Tbody>
      </Table>
    </Box>
  );
};

export default FileTable;
