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
      <HStack width="100%" bg={headerColor} alignItems="center" p="30px">
        <Box width="160px" />
        <Box
          position="absolute"
          left="50%"
          transform="translateX(-50%)"
          fontSize="32px"
          fontWeight="bold"
        >
          Orison AI
        </Box>
        {/* <ColorModeToggle /> */}
      </HStack>
      <Center height="100%">
        <VStack maxHeight="90%">
          <Text fontSize="36px" mb="64px">{isSignUp ? "Let's get started." : "Welcome back."}</Text>
          <Box p="16px" borderWidth="1px" borderRadius="10px" overflow="hidden" minW="400px" maxW="90%">
            {isSignUp ? <SignUpForm /> : <LogInForm />}
          </Box>
          <Text fontSize="22px">
            Don't have an account? Contact us on{" "}
            <Text as="span" fontSize="24px" fontWeight="bold">
              contact@orison.ai
            </Text>{" "}
            for a free demo
          </Text>
          {/* <Link variant="link" mt="22px" onClick={() => setSignUp(!isSignUp)}>
            {isSignUp ? "Already have an account? Login." : "Don't have an account? Create one by contacting us on contact@orison.ai"}
          </Link> */}
        </VStack>
      </Center>
    </VStack>
  );
};

export default Auth;
