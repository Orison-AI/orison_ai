// ./components/SignUp.jsx

// React
import React, { useState } from 'react';

// Firebase
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

// Chakra
import {
  Input,
  Button,
  FormControl,
  FormLabel,
  VStack,
  useToast
} from "@chakra-ui/react";

const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const auth = getAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in
        const user = userCredential.user;
        toast({
          title: "Signed In",
          description: `You have successfully signed in: ${user}`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
        // Additional actions upon successful sign in, like redirecting
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        toast({
          title: "Error Signing In",
          description: `${errorCode}: ${errorMessage}`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        // Handle errors here, such as displaying a notification
      });
  };

  return (
    <VStack as="form" onSubmit={handleSubmit} spacing={4}>
      <FormControl isRequired>
        <FormLabel htmlFor='email'>Email</FormLabel>
        <Input id='email' type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </FormControl>
      <FormControl isRequired>
        <FormLabel htmlFor='password'>Password</FormLabel>
        <Input id='password' type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </FormControl>
      <Button type="submit" colorScheme="blue">Sign In</Button>
    </VStack>
  );
};

export default SignIn;
