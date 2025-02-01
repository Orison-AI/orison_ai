// ./components/Navigation.jsx

// React
import React from 'react';

// Chakra
import {
  Box, HStack, Select, Text,
} from '@chakra-ui/react';
import { ChevronRightIcon } from '@chakra-ui/icons';

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
    const selected = applicants.find(app => app.id === event.target.value);
    setSelectedApplicant(selected);
  };

  const handleViewChange = (event) => {
    setCurrentView(event.target.value);
  };

  const viewDisplayNames = {
    [Views.MANAGE_APPLICANTS]: "Manage Applicants",
    [Views.APPLICANT_DOCUMENTS]: "Documents",
    // [Views.QUESTIONAIRE]: "Questionnaire",
    [Views.APPLICANT_SUMMARIZATION]: "Summarization",
    // [Views.EVIDENCE]: "EvidenceLetter",
    [Views.DOCASSIST]: "DocAssist",
  };

  // Generate options in the same order as `viewDisplayNames`
  const viewOptions = Object.keys(viewDisplayNames)
    .filter(viewKey => viewKey !== Views.MANAGE_APPLICANTS)
    .map(viewKey => (
      <option key={viewKey} value={viewKey}>
        {viewDisplayNames[viewKey]}
      </option>
    ));


  const renderCurrentViewNav = () => {
    switch (currentView) {
      case Views.MANAGE_APPLICANTS:
        return (
          <Text className="oai-nav-manage" alignSelf="flex-start" m="0" fontSize="32px">
            {viewDisplayNames[Views.MANAGE_APPLICANTS]}
          </Text>
        );
      // case Views.QUESTIONAIRE:
      //   return (
      //     <Text className="oai-nav-questionaire" alignSelf="flex-start" m="0" fontSize="32px">
      //       {viewDisplayNames[Views.QUESTIONAIRE]}
      //     </Text>
      //   );
      default:
        return (
          <HStack className="oai-nav-non-manage" width="100%" m="0">
            <Select
              size='lg'
              width="200px"
              value={selectedApplicant ? selectedApplicant.id : ""}
              onChange={handleApplicantChange}
            >
              {applicants.map((app) => (
                <option key={app.id} value={app.id}>{app.name}</option>
              ))}
            </Select>
            <ChevronRightIcon w="32px" h="32px" />
            <Select
              size='lg'
              width="200px"
              value={currentView}
              onChange={handleViewChange}
            >
              {viewOptions}
            </Select>
          </HStack>
        );
    }
  };

  return (
    <Box className="oai-nav" ref={ref} width="100%" mb="24px" color="blue.100">
      {renderCurrentViewNav()}
    </Box>
  );
});

export default Navigation;
