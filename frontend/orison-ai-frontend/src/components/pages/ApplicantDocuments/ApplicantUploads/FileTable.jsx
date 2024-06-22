// ./components/pages/ApplicantDocuments/ApplicantUploads/FileTable.jsx

// React
import React from 'react';

// Chakra UI
import {
    Badge, Box, Button, IconButton,
    Table, Thead, Tbody, Tr, Th, Td,
} from '@chakra-ui/react';
import { CloseIcon, CheckCircleIcon } from '@chakra-ui/icons';

const FileTable = ({
  documents,
  processedFiles,
  vectorizeFile,
  deleteFile,
  viewFile,
  isVectorizing,
}) => {
  return (
    <Box mb="2vh" width="100%" overflowY="auto" overflowX="auto" border="1px" borderColor="gray.600" borderRadius="1vh">
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
              <Td>
                {fileName} 
                {(processedFiles.includes(fileName)) && (
                  <CheckCircleIcon ml="2" color="green.500" />
                )}
              </Td>
              <Td>
                {processedFiles.includes(fileName) ? (
                  <Badge colorScheme="green">Vectorized</Badge>
                ) : (
                  <Badge colorScheme="orange">Not Vectorized</Badge>
                )}
              </Td>
              <Td isNumeric>
                <Button
                  ml="2vh"
                  colorScheme="blue"
                  onClick={() => vectorizeFile(fileName)}
                  isDisabled={isVectorizing}
                >
                  Vectorize
                </Button>
                <Button ml="2vh" onClick={() => viewFile(fileName)}>
                  View
                </Button>
                <IconButton
                  icon={<CloseIcon />}
                  ml="2vh"
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
