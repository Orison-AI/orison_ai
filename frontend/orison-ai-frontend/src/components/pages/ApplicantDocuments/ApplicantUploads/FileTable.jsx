import React from 'react';
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
  deleteAllFiles,
  viewFile,
  vectorizingFiles,
  vectorizeStatus,
}) => {
  return (
    <Box
      mb="10px"
      width="100%"
      overflowX="auto"
      border="1px"
      borderColor="gray.600"
      borderRadius="10px"
    >
      <Table variant="simple" tableLayout="fixed" width="100%">
        <Thead>
          <Tr>
            <Th width="40%">File Name</Th>
            <Th width="20%">Status</Th>
            <Th width="40%">
              <HStack spacing={4} justifyContent="flex-end">
                <Button
                  colorScheme="blue"
                  onClick={vectorizeAllFiles}
                  isDisabled={documents.every(doc => doc.vectorized)}
                >
                  Vectorize All
                </Button>
                <Button colorScheme="red" onClick={unvectorizeAllFiles}>
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
                      await deleteAllFiles();
                    }
                  }}
                  isDisabled={documents.length === 0}
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
                {/* Ensure long filenames wrap */}
                <Td wordBreak="break-word" whiteSpace="normal">
                  {fileName}
                </Td>

                <Td whiteSpace="nowrap">
                  {vectorized ? (
                    <Badge colorScheme="green">Vectorized</Badge>
                  ) : (
                    <Badge colorScheme="orange">Not Vectorized</Badge>
                  )}
                </Td>

                {/* Ensure action buttons stay within table boundaries */}
                <Td whiteSpace="normal">
                  <HStack spacing={2} flexWrap="wrap" justifyContent="flex-end">
                    {isVectorizing && vectorizeStatus === 'loading' && (
                      <Spinner color="blue.500" size="sm" />
                    )}
                    {isVectorizing && vectorizeStatus === 'success' && (
                      <CheckCircleIcon color="green.500" />
                    )}
                    {isVectorizing && vectorizeStatus === 'error' && (
                      <WarningIcon color="red.500" />
                    )}

                    <Button
                      colorScheme="blue"
                      onClick={() => vectorizeFile(fileName)}
                      isDisabled={isVectorizing || vectorized}
                    >
                      Vectorize
                    </Button>

                    <Button
                      colorScheme="red"
                      onClick={() => unvectorizeFile(fileName)}
                      isDisabled={!vectorized}
                      style={{ visibility: !vectorized ? 'hidden' : 'visible' }}
                    >
                      Unvectorize
                    </Button>

                    <Button onClick={() => viewFile(fileName)} isDisabled={isVectorizing}>
                      View
                    </Button>

                    <IconButton
                      icon={<CloseIcon />}
                      colorScheme="red"
                      variant="ghost"
                      onClick={() => deleteFile(fileName)}
                      isDisabled={isVectorizing}
                    />
                  </HStack>
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
