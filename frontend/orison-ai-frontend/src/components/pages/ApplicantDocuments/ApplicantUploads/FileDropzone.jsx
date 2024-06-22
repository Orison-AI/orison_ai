// ./components/pages/ApplicantDocuments/ApplicantUploads/FileUploader/FileDropzone.jsx

// React
import React from 'react';

// Dropzone
import { useDropzone } from 'react-dropzone';

// Chakra UI
import { VStack, Icon, Text, Link } from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

const FileDropzone = ({ onDrop }) => {
  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({ onDrop });

  return (
    <VStack
      {...getRootProps()}
      border="2px dashed gray"
      w="100%"
      p="20px"
      mb="20px"
      backgroundColor={isDragActive ? 'gray.700' : 'transparent'}
    >
      <input {...getInputProps()} />
      <Icon as={DownloadIcon} color="gray.500" />
      <Text fontSize="20px">
        <Link as="b" onClick={open} cursor="pointer">Choose a file</Link> or drag it here
      </Text>
    </VStack>
  );
};

export default FileDropzone;
