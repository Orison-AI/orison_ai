// ./components/auth/Auth.jsx

// React
import React, { useState } from 'react';

// Firebase
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";

// Chakra
import {
  Box, Button, Center, FormControl, FormLabel,
  Input, Link, Text, useToast, VStack,
} from "@chakra-ui/react";

const Auth = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const auth = getAuth();
  const [isSignUp, setSignUp] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    const action = isSignUp ? createUserWithEmailAndPassword : signInWithEmailAndPassword;
    action(auth, email, password)
      .then((userCredential) => {
        toast({
          title: `Successfully ${isSignUp ? 'signed up' : 'signed in'}`,
          description: `Welcome ${isSignUp ? 'aboard' : 'back'}!`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      })
      .catch((error) => {
        toast({
          title: `Error ${isSignUp ? 'signing up' : 'signing in'}`,
          description: `${error.message}`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      });
  };

  return (
    <VStack>
      <Center width="100%" bg="rgba(23, 25, 35, 0.80)">
        <Box fontSize="3vh" p="1vh">orison.ai</Box>
      </Center>
      <Center height="100vh">
        <VStack>
          <Text fontSize="3.5vh" mb="8vh">{isSignUp ? "Let's get started." : "Welcome back."}</Text>
          <Box p="2vh" borderWidth="1px" borderRadius="10px" overflow="hidden" minW="30vh" maxW="50vh">
            <VStack as="form" onSubmit={handleSubmit} spacing={4}>
              <FormControl isRequired>
                <FormLabel htmlFor='email'>Email</FormLabel>
                <Input id='email' type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </FormControl>
              <FormControl isRequired>
                <FormLabel htmlFor='password'>Password</FormLabel>
                <Input id='password' type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </FormControl>
              <Button type="submit" colorScheme="blue" mt="2vh">{isSignUp ? "Sign Up" : "Sign In"}</Button>
            </VStack>
          </Box>
          <Link color="blue.500" mt="2vh" onClick={() => setSignUp(!isSignUp)}>
            {isSignUp ? "Already have an account? Sign in." : "Don't have an account? Create one."}
          </Link>
        </VStack>
      </Center>
    </VStack>
  );
};

export default Auth;
