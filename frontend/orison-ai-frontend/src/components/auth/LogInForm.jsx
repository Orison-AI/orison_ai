// ./components/auth/LogInForm.jsx

// React
import React, { useState } from 'react';

// Firebase
import { signInWithEmailAndPassword } from "firebase/auth";

// Chakra
import {
  Button, FormControl, FormLabel, Input, useToast, VStack,
} from "@chakra-ui/react";

// Internal
import { auth } from '../../common/firebaseConfig';

const LogInForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();

  const handleSubmit = (e) => {
    e.preventDefault();
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        toast({
          title: "Logged In",
          description: "You have successfully logged in.",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      })
      .catch((error) => {
        toast({
          title: "Error Logging In",
          description: `${error.message}`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      });
  };

  return (
    <VStack as="form" onSubmit={handleSubmit} spacing={4}>
      <FormControl isRequired>
        <FormLabel>Email</FormLabel>
        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </FormControl>
      <FormControl isRequired>
        <FormLabel>Password</FormLabel>
        <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </FormControl>
      <Button mt="16px" type="submit" colorScheme="blue">Login</Button>
    </VStack>
  );
};

export default LogInForm;
