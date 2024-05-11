// ./components/auth/LogInForm.jsx

// React
import React, { useState } from 'react';

// Firebase
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

// Chakra
import {
  Button, FormControl, FormLabel, Input, useToast, VStack,
} from "@chakra-ui/react";

const LogInForm = ({ initialEmail, setLoginEmail }) => {
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState('');
  const toast = useToast();
  const auth = getAuth();

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
        setLoginEmail(email);
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
      <Button mt="2vh" type="submit" colorScheme="blue">Login</Button>
    </VStack>
  );
};

export default LogInForm;
