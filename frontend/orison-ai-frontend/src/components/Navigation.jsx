// ./components/Navigation.jsx

// React
import React from 'react';

// Chakra
import {
  HStack, Text, Select,
} from '@chakra-ui/react';

const Navigation = ({ 
  applicants,
  selectedApplicant,
  setSelectedApplicant,
  currentView,
  setCurrentView,
}) => {
  const handleApplicantChange = (event) => {
    const selectedApplicant = applicants.find(app => app.id === event.target.value);
    setSelectedApplicant(selectedApplicant);
  };

  return (
    <HStack width="100%" ml="16px" mb="32px" fontSize="32px" color="gray.200">
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
};

export default Navigation;

