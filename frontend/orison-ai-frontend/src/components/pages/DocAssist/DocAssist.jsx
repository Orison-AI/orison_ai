import React, { useState } from 'react';
import { Box, Button, Input, VStack, Text, HStack, Flex } from '@chakra-ui/react';

const DocAssist = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);

    const handleSendMessage = async () => {
        if (inputMessage.trim() !== '') {
            setMessages((prevMessages) => [...prevMessages, { text: inputMessage, sender: 'user' }]);
            setInputMessage('');
            setIsStreaming(true);

            // Mock streaming response for example purposes
            setTimeout(() => {
                setMessages((prevMessages) => [...prevMessages, { text: 'This is a response chunk from the bot.', sender: 'bot' }]);
                setIsStreaming(false);
            }, 1000);
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
                        placeholder="Type your message..."
                        bg="gray.700"
                        borderRadius="md"
                        color="white"
                        _placeholder={{ color: 'gray.400' }}
                        flex="1"
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
