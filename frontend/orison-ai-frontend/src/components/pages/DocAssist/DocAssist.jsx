import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Button, Input, VStack, Text, HStack, Flex, Spinner, useToast } from '@chakra-ui/react';
import { docassist } from '../../../api/api';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import { collection, orderBy, limit, query, getDocs } from 'firebase/firestore';
import ReactMarkdown from 'react-markdown';
import Select, { components } from 'react-select';

const DocAssist = ({ selectedApplicant }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const toast = useToast();
    const [user] = useAuthState(auth);

    const fetchChatHistory = useCallback(async () => {
        if (user && selectedApplicant) {
            const querySnapshot = await getDocs(query(collection(db, "chat_memory", user.uid, selectedApplicant.id), orderBy("timestamp", "desc"), limit(1)));
            const docSnap = querySnapshot.docs[0];
            if (docSnap && docSnap.exists()) {
                const history = docSnap.data().history || [];

                // Sort history by timestamp in ascending order
                const sortedHistory = history.sort((a, b) => a.timestamp.toMillis() - b.timestamp.toMillis());

                // Format messages for display
                const formattedMessages = sortedHistory.map(entry => [
                    { text: entry.user_message, sender: 'user' },
                    { text: entry.assistant_response, sender: 'bot' }
                ]).flat();

                setMessages(formattedMessages);
            } else {
                console.error("No chat history found for the selected applicant.");
            }
        }
    }, [user, selectedApplicant]);

    useEffect(() => {
        fetchChatHistory(); // Fetch chat history on component mount or when user/selectedApplicant changes
    }, [fetchChatHistory]);

    const handleSendMessage = async () => {
        if (inputMessage.trim() === '') {
            toast({
                title: "Error",
                description: "Please enter a message.",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        if (!user || !selectedApplicant) {
            toast({
                title: "Error",
                description: "User or selected applicant not found.",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        setInputMessage('');
        setIsStreaming(true);

        try {
            await docassist(user.uid, selectedApplicant.id, inputMessage);

            // Fetch updated history after sending the message
            await fetchChatHistory();
        } catch (error) {
            console.error('Error:', error);
            toast({
                title: "Error",
                description: error.message || "Failed to get response from AI.",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setIsStreaming(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !isStreaming) {
            handleSendMessage();
        }
    };

    return (
        <Flex direction="column" height="100%" bg="gray.900">
            {/* Chat Display Area */}
            <VStack
                flex="1"
                spacing="4"
                p="4"
                overflowY="auto"
                width="100%"
                align="stretch"
                bg="gray.800"
            >
                {messages.map((msg, idx) => (
                    <MessageCard key={idx} message={msg} />
                ))}
                {isStreaming && (
                    <HStack justify="flex-start">
                        <Spinner size="sm" color="white" />
                        <Text color="white">AI is processing your request...</Text>
                    </HStack>
                )}
            </VStack>

            {/* Input Area at Bottom */}
            <Box
                p="4"
                bg="gray.800"
                borderTop="1px solid"
                borderColor="gray.700"
                width="100%"
            >
                <HStack width="100%">
                    {/* Input Message Box */}
                    <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Hello I'm your AI assistant. How can I help you today?"
                        bg="gray.700"
                        borderRadius="md"
                        color="white"
                        _placeholder={{ color: 'gray.400' }}
                        flex="1"
                        isDisabled={isStreaming}
                    />

                    {/* Send Button */}
                    <Button colorScheme="blue" onClick={handleSendMessage} isDisabled={isStreaming}>
                        Send
                    </Button>
                </HStack>
            </Box>
        </Flex>
    );
};

export default DocAssist;

// MessageCard component
const MessageCard = ({ message }) => {
    const { text, sender } = message;

    return (
        <HStack justify={sender === 'user' ? 'flex-end' : 'flex-start'} width="100%">
            <Box
                bg={sender === 'user' ? 'blue.700' : 'gray.900'}
                color="white"
                borderRadius="md"
                p="3"
                pl="4"
                maxWidth={sender === 'user' ? "75%" : "100%"}
                wordBreak="break-word"
            >
                <ReactMarkdown
                    components={{
                        p: ({ node, ...props }) => <Text mb={2} {...props} />,
                        strong: ({ node, ...props }) => <Text as="b" {...props} />,
                        em: ({ node, ...props }) => <Text as="i" {...props} />,
                        ul: ({ node, ...props }) => <Box as="ul" pl="4" mb={2} {...props} />,
                        li: ({ node, ...props }) => <Text as="li" mb={1} {...props} />,
                        ol: ({ node, ...props }) => <Box as="ol" pl="4" mb={2} {...props} />,
                    }}
                >
                    {text}
                </ReactMarkdown>
            </Box>
        </HStack>
    );
};
