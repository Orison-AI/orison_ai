import React, { useState } from 'react';
import { Box, Button, Input, VStack, Text, HStack, Flex, Spinner, useToast } from '@chakra-ui/react';
import { docassist } from '../../../api/api.jsx';  // Import your API function here
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../../../common/firebaseConfig';

const DocAssist = ({ selectedApplicant }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [timeoutDuration, setTimeoutDuration] = useState(10000); // Timeout duration (in milliseconds)
    const toast = useToast(); // Toast for showing error messages
    const [user] = useAuthState(auth);

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

        setMessages((prevMessages) => [...prevMessages, { text: inputMessage, sender: 'user' }]);
        setInputMessage('');
        setIsStreaming(true);
        try {
            const response = await Promise.race([
                docassist(user.uid, selectedApplicant.id, "research", inputMessage),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Request timed out')), timeoutDuration))
            ]);

            setMessages((prevMessages) => [...prevMessages, { text: response.message, sender: 'bot' }]);
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
                    <HStack key={idx} justify={msg.sender === 'user' ? 'flex-end' : 'flex-start'}>
                        <Text
                            bg={msg.sender === 'user' ? 'blue.500' : 'gray.600'}
                            color="white"
                            borderRadius="md"
                            p="3"
                            maxWidth="75%"
                            wordBreak="break-word"
                        >
                            {msg.text}
                        </Text>
                    </HStack>
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
                    <Button colorScheme="blue" onClick={handleSendMessage} isDisabled={isStreaming}>
                        Send
                    </Button>
                </HStack>
            </Box>
        </Flex>
    );
};

export default DocAssist;
