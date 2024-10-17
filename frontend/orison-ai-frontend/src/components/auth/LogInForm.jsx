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
  const toast = useToast();

  const handleLogin = async (user) => {
    try {
      // Check if 'eb1_a_questionnaire' exists for the logged-in user
      const attorneyDocRef = doc(db, "templates", "attorneys", user.uid, "eb1_a_questionnaire");
      const attorneyDoc = await getDoc(attorneyDocRef);

      // Step 2: If the document doesn't exist or 'eb1_a_questionnaire' field is missing, copy from default template
      if (!attorneyDoc.exists() || !attorneyDoc.data().eb1_a_questionnaire) {
        // Step 3: Get the default questionnaire from the template
        const defaultQuestionnaireRef = doc(db, "templates", "eb1_a_questionnaire");
        const defaultQuestionnaireDoc = await getDoc(defaultQuestionnaireRef);

        if (defaultQuestionnaireDoc.exists()) {
          const defaultQuestionnaire = defaultQuestionnaireDoc.data();
          await setDoc(attorneyDocRef, defaultQuestionnaire);

          console.log("Default questionnaire copied to the attorney's document.");
          toast({
            title: "Questionnaire Created",
            description: "The default questionnaire has been copied to your profile.",
            status: "info",
            duration: 5000,
            isClosable: true,
          });
        } else {
          console.error("Default questionnaire template not found.");
        }
      } else {
        console.log("eb1_a_questionnaire already exists for this attorney.");
      }

      // Show login success toast
      toast({
        title: "Logged In",
        description: "You have successfully logged in.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error("Error checking/creating eb1_a_questionnaire: ", error);
      toast({
        title: "Error",
        description: `Error checking or creating the questionnaire: ${error.message}`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        handleLogin(user);  // Check for the 'eb1_a_questionnaire' after logging in
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
