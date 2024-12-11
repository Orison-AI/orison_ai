// ./components/pages/Evidence/Evidence.jsx

// React
import React, { useCallback, useEffect, useState } from "react";

// Firebase
import { useAuthState } from "react-firebase-hooks/auth";
import { auth, db } from "../../../common/firebaseConfig";
import {
    collection,
    getDocs,
    orderBy,
    query,
    limit,
    doc,
} from "firebase/firestore";

// Chakra UI
import {
    Box,
    Button,
    Center,
    HStack,
    Text,
    useToast,
    VStack,
    Spinner,
} from "@chakra-ui/react";
import { CheckCircleIcon, WarningIcon } from "@chakra-ui/icons";

// Demo AI
import { evidence } from "../../../api/api"; // Replace with your API function for generating evidence
import { useApplicantContext } from "../../../context/ApplicantContext";

const Evidence = () => {
    const [user] = useAuthState(auth);
    const [evidenceDataStatus, setEvidenceDataStatus] = useState("");
    const [evidenceData, setEvidenceData] = useState(null);
    const [evidenceProgress, setEvidenceProgress] = useState("");
    const toast = useToast();
    const { selectedApplicant } = useApplicantContext();
    const [lastUpdated, setLastUpdated] = useState('');

    // Fetch the latest evidence letter
    const fetchEvidenceData = useCallback(async () => {
        if (user && selectedApplicant) {
            setEvidenceDataStatus("loading");
            const evidenceQuery = query(
                collection(
                    doc(collection(db, "evidence_letter"), user.uid),
                    selectedApplicant.id
                ),
                orderBy("date_created", "desc"),
                limit(1)
            );
            const querySnapshot = await getDocs(evidenceQuery);
            if (querySnapshot.empty) {
                setEvidenceData(null);
                setEvidenceDataStatus("not_found");
                setLastUpdated(''); // Reset timestamp when no data is found
            } else {
                const data = querySnapshot.docs[0].data();
                setEvidenceData(data);
                setEvidenceDataStatus("found");
                // Update the last updated timestamp
                const timestamp = data.date_created.toDate(); // Firestore timestamp to JS Date
                setLastUpdated(new Intl.DateTimeFormat('en-US', {
                    dateStyle: 'medium',
                    timeStyle: 'short',
                }).format(timestamp));
            }
        }
    }, [user, selectedApplicant]);

    useEffect(() => {
        fetchEvidenceData();
    }, [fetchEvidenceData, selectedApplicant]);

    // Generate new evidence letter
    const handleGenerateEvidence = async () => {
        if (selectedApplicant) {
            try {
                setEvidenceProgress("loading");
                await evidence(user.uid, selectedApplicant.id); // Call your evidence API function
                setEvidenceProgress("success");
                toast({
                    title: "Evidence Generated",
                    description: `Evidence letter generated successfully for ${selectedApplicant.name}`,
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                });
                await fetchEvidenceData();
            } catch (error) {
                setEvidenceProgress("error");
                toast({
                    title: "Generation Failed",
                    description: error.message,
                    status: "error",
                    duration: 5000,
                    isClosable: true,
                });
            }
        }
    };

    return (
        <Box className="oai-evidence" height="100%" width="100%">
            <Center width="100%" flex="1">
                <VStack height="100%" width="100%">
                    <HStack className="oai-evidence-generate-stack" mb="20px" justifyContent="flex-start">
                        <Button
                            onClick={handleGenerateEvidence}
                            colorScheme="green"
                            isDisabled={evidenceProgress === "loading"}
                            mr="10px"
                            mb="8px"
                        >
                            Generate Evidence Letter
                        </Button>
                        {evidenceProgress === "loading" && (
                            <Spinner color="blue.500" size="sm" />
                        )}
                        {evidenceProgress === "success" && (
                            <Box boxSize="24px">
                                <CheckCircleIcon color="green.500" boxSize="100%" />
                            </Box>
                        )}
                        {evidenceProgress === "error" && (
                            <Box boxSize="24px">
                                <WarningIcon color="red.500" boxSize="100%" />
                            </Box>
                        )}
                    </HStack>
                    {evidenceDataStatus === 'found' && (
                        <>
                            <Text fontSize="sm" color="gray.500">
                                Last Updated: {lastUpdated}
                            </Text>
                        </>
                    )}
                    {evidenceDataStatus === "found" && (
                        <Box
                            padding="20px"
                            borderRadius="md"
                            backgroundColor="gray.900"
                            border="1px solid"
                            borderColor="gray.700"
                            color="whiteAlpha.900"
                            width="80%"
                        >
                            {evidenceData.summary.split("\n").map((paragraph, index) => (
                                <Text key={index} marginBottom="10px">
                                    {paragraph.split("**").map((chunk, i) =>
                                        i % 2 === 0 ? chunk : <strong key={i}>{chunk}</strong>
                                    )}
                                </Text>
                            ))}
                        </Box>
                    )}
                    {evidenceDataStatus === "loading" && (
                        <Box
                            className="oai-evidence-loading"
                            bg="gray.900"
                            p="20px"
                            borderRadius="20px"
                            width="60%"
                            minWidth="600px"
                        >
                            <Text color="whiteAlpha.900">Loading evidence letter data...</Text>
                        </Box>
                    )}
                    {evidenceDataStatus === "not_found" && (
                        <Box
                            className="oai-evidence-not-found"
                            bg="gray.900"
                            p="20px"
                            borderRadius="20px"
                            width="60%"
                            minWidth="600px"
                        >
                            <Text color="whiteAlpha.900">No evidence letter data found.</Text>
                        </Box>
                    )}
                </VStack>
            </Center>
        </Box>
    );
};

export default Evidence;
