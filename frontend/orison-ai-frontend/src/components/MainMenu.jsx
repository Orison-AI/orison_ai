// ./components/MainMenu.jsx

// External
import React from 'react';
import {
  Button, Divider,
  Drawer, DrawerOverlay, DrawerContent,
  DrawerCloseButton, DrawerHeader, DrawerBody,
  Select, useColorMode, VStack,
} from '@chakra-ui/react';

// Internal
import Views from '../common/views';

const MainMenu = ({
  isOpen,
  onClose,
  changeView,
  applicants,
  selectedApplicant,
  setSelectedApplicant,
}) => {

  const { colorMode } = useColorMode();
  const buttonHoverColor = colorMode === "light" ? "gray.100" : "gray.600";

  const MenuButton = ({label, onClick, disabled = false}) => (
    <Button 
      variant="ghost"
      width="100%"
      justifyContent="flex-start"
      onClick={onClick}
      _hover={{ bg: buttonHoverColor }}
      isDisabled={disabled}
    >
      {label}
    </Button>
  );

  return (
    <Drawer isOpen={isOpen} onClose={onClose} placement="left">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>orison.ai</DrawerHeader>
        <DrawerBody pl="4vh">
          <VStack spacing={4}>
            <MenuButton label="Manage Applicants" onClick={() => changeView(Views.MANAGE_APPLICANTS)} />
            <Divider/>
            <Select
              placeholder="Select an applicant"
              value={selectedApplicant ? selectedApplicant.id : undefined}
              onChange={e => {
                setSelectedApplicant(applicants.find(app => app.id === e.target.value));
              }}
            >
              {applicants.map(app => (
                <option key={app.id} value={app.id}>{app.name}</option>
              ))}
            </Select>
            <MenuButton label="Documents" disabled={!selectedApplicant} onClick={() => changeView(Views.APPLICANT_DOCUMENTS)} />
            <MenuButton label="Summarization" disabled={!selectedApplicant} onClick={() => changeView(Views.APPLICANT_SUMMARIZATION)} />
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
}

export default MainMenu;
