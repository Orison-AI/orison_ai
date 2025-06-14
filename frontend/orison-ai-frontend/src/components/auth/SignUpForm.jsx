// ./components/auth/SignUpForm.jsx

// React
import React, { useState } from 'react';

// Firebase
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, getDoc, setDoc } from 'firebase/firestore';

// Chakra
import {
  Button, FormControl, FormErrorMessage, FormLabel,
  Input, useToast, VStack,
} from "@chakra-ui/react";

// Internal
import { auth, db } from '../../common/firebaseConfig';

const SignUpForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const toast = useToast();

  const validatePassword = () => {
    let errors = [];
    if (password.length < 8) {
      errors.push("Password must be at least 8 characters.");
    }
    if (!/[A-Z]/.test(password)) {
      errors.push("Password must contain at least one uppercase letter.");
    }
    if (!/[a-z]/.test(password)) {
      errors.push("Password must contain at least one lowercase letter.");
    }
    if (!/[0-9]/.test(password)) {
      errors.push("Password must contain at least one number.");
    }
    if (!/[!@#$%^&*]/.test(password)) {
      errors.push("Password must contain at least one special character (!@#$%^&*).");
    }
    if (password !== confirmPassword) {
      errors.push("Passwords do not match.");
    }
    setError(errors.join(" "));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    validatePassword();
    if (error) return;
  };

  return (
    <VStack as="form" onSubmit={handleSubmit} spacing={4}>
      <FormControl isRequired>
        <FormLabel>Email</FormLabel>
        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </FormControl>
      <FormControl isRequired isInvalid={!!error}>
        <FormLabel>Password</FormLabel>
        <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <FormErrorMessage>{error}</FormErrorMessage>
      </FormControl>
      <FormControl isRequired isInvalid={!!error}>
        <FormLabel>Confirm Password</FormLabel>
        <Input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
        <FormErrorMessage>{error}</FormErrorMessage>
      </FormControl>
      <Button mt="16px" type="submit" colorScheme="blue" isDisabled={!email || !password || !confirmPassword}>Sign Up</Button>
    </VStack>
  );
};

export default SignUpForm;
