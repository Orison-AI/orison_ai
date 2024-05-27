// ./components/auth/Auth.jsx

// React
import React, { useState } from 'react';

// Chakra
import {
  Box, Center, HStack, Link, Text, useColorModeValue, VStack,
} from "@chakra-ui/react";

// Internal
import ColorModeToggle from "../settings/ColorModeToggle";
import LogInForm from './LogInForm';
import SignUpForm from './SignUpForm';

const Auth = () => {
  const [isSignUp, setSignUp] = useState(false);
  const headerColor = useColorModeValue("rgba(23, 25, 35, 0.10)", "rgba(23, 25, 35, 0.90)");

  return (
    <VStack width="100%" height="100%">
      <HStack width="100%" bg={headerColor}>
        <Box width="20vh" />
        <Center width="100%">
          <Box fontSize="32px" p="1vh">orison.ai</Box>
        </Center>
        <ColorModeToggle />
      </HStack>
      <Center height="100%">
        <VStack maxHeight="90%">
          <Text fontSize="36px" mb="8vh">{isSignUp ? "Let's get started." : "Welcome back."}</Text>
          <Box p="2vh" borderWidth="1px" borderRadius="10px" overflow="hidden" minW="400px" maxW="90%">
            {isSignUp ? <SignUpForm /> : <LogInForm />}
          </Box>
          <Link variant="link" mt="2vh" onClick={() => setSignUp(!isSignUp)}>
            {isSignUp ? "Already have an account? Login." : "Don't have an account? Create one."}
          </Link>
        </VStack>
      </Center>
    </VStack>
  );
};

export default Auth;
