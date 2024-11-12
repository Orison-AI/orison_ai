// React
import React, { useState } from 'react';

// Firebase
import { signInWithEmailAndPassword } from "firebase/auth";
import { doc, getDoc, setDoc } from "firebase/firestore";

// Chakra
import {
  Button, FormControl, FormLabel, Input, useToast, VStack,
} from "@chakra-ui/react";

// Internal
import { auth, db } from '../../common/firebaseConfig'; // Assuming db is your Firestore instance

const LogInForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    signInWithEmailAndPassword(auth, email, password);
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
