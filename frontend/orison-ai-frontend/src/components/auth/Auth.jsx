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

// TODO: Fix re-rendering of forms whenever email changes. This breaks the form behavior.

const Auth = () => {
  const [email, setEmail] = useState('');
  const [isSignUp, setSignUp] = useState(true);
  const headerColor = useColorModeValue("rgba(23, 25, 35, 0.10)", "rgba(23, 25, 35, 0.90)");

  const Form = () => (
    isSignUp
      ? <SignUpForm initialEmail={email} setLoginEmail={setEmail} />
      : <LogInForm initialEmail={email} setLoginEmail={setEmail} />
  );

  return (
    <VStack width="100%">
      <HStack width="100%" bg={headerColor}>
        <Box width="20vh" />
        <Center width="100%">
          <Box fontSize="3vh" p="1vh">orison.ai</Box>
        </Center>
        <ColorModeToggle />
      </HStack>
      <Center height="70vh">
        <VStack>
          <Text fontSize="3.5vh" mb="8vh">{isSignUp ? "Let's get started." : "Welcome back."}</Text>
          <Box p="2vh" borderWidth="1px" borderRadius="10px" overflow="hidden" minW="30vh" maxW="50vh">
            {<Form />}
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
