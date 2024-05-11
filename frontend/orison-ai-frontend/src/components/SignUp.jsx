// ./components/SignUp.jsx

// React
import React, { useState } from 'react';

// Firebase
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";

// Chakra
import {
  Input,
  Button,
  FormControl,
  FormLabel,
  VStack,
  useToast
} from "@chakra-ui/react";

const SignUp = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const auth = getAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in 
        const user = userCredential.user;
        toast({
          title: "Account created.",
          description: `Your account has been successfully created: ${user}`,
          status: "success",
          duration: 9000,
          isClosable: true,
        });
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        toast({
          title: "Error creating account",
          description: `${errorCode}: ${errorMessage}`,
          status: "error",
          duration: 9000,
          isClosable: true,
        });
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
      <Button type="submit" colorScheme="blue">Sign Up</Button>
    </VStack>
  );
};

export default SignUp;
