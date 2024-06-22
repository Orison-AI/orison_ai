// ./components/pages/ApplicantDocuments/ApplicantUploads/FileTable.jsx

// React
import React from 'react';

// Chakra UI
import {
    Badge, Box, Button, IconButton, Spinner,
    Table, Thead, Tbody, Tr, Th, Td,
} from '@chakra-ui/react';
import { CheckCircleIcon, CloseIcon, WarningIcon } from '@chakra-ui/icons';

const FileTable = ({
  documents,
  vectorizeFile,
  deleteFile,
  viewFile,
  vectorizingFile,
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
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody fontSize="16px">
          {documents.map(fileName => (
            <Tr key={fileName}>
              <Td whiteSpace="nowrap">
                {fileName}
              </Td>
              <Td whiteSpace="nowrap">
                {vectorizingFile === fileName && vectorizeStatus === 'success' ? (
                  <Badge colorScheme="green">Vectorized</Badge>
                ) : (
                  <Badge colorScheme="orange">Not Vectorized</Badge>
                )}
              </Td>
              <Td isNumeric whiteSpace="nowrap">
                {vectorizingFile === fileName && vectorizeStatus === 'loading' && <Spinner color="blue.500" size="sm" />}
                {vectorizingFile === fileName && vectorizeStatus === 'success' && <CheckCircleIcon color="green.500" />}
                {vectorizingFile === fileName && vectorizeStatus === 'error' && <WarningIcon color="red.500" />}
                <Button
                  ml="16px"
                  colorScheme="blue"
                  onClick={() => vectorizeFile(fileName)}
                  isDisabled={vectorizeStatus === 'loading'}
                >
                  Vectorize
                </Button>
                <Button ml="16px" onClick={() => viewFile(fileName)}>
                  View
                </Button>
                <IconButton
                  icon={<CloseIcon />}
                  ml="16px"
                  colorScheme="red"
                  variant="ghost"
                  onClick={() => deleteFile(fileName)}
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default FileTable;
