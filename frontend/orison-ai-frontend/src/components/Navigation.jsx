// ./components/Navigation.jsx

// React
import React from 'react';

// Chakra
import {
  Box, HStack, Select, Text,
} from '@chakra-ui/react';

// Orison
import Views from '../common/views';

const Navigation = React.forwardRef(({ 
  applicants,
  selectedApplicant,
  setSelectedApplicant,
  currentView,
  setCurrentView,
}, ref) => {
  const handleApplicantChange = (event) => {
    const selectedApplicant = applicants.find(app => app.id === event.target.value);
    setSelectedApplicant(selectedApplicant);
  };

  const navContent = currentView === Views.MANAGE_APPLICANTS ? (
    <Text className="oai-nav-manage" alignSelf="flex-start" m="0">
      Manage Applicants
    </Text>
  ) : (
    <HStack className="oai-nav-non-manage" width="100%" m="0">
      <Select 
        width="200px"
        value={selectedApplicant ? selectedApplicant.id : ""}
        onChange={handleApplicantChange}
      >
        {applicants.map((app) => (
          <option key={app.id} value={app.id}>{app.name}</option>
        ))}
      </Select>
      <Text>&gt;</Text>
      <Text color="green.300" as="strong">Documents</Text>
    </HStack>
  );

  return (
    <Box className="oai-nav" ref={ref} width="100%" mb="24px" fontSize="32px" color="gray.200">
      {navContent}
    </Box>
  );
});

export default Navigation;

