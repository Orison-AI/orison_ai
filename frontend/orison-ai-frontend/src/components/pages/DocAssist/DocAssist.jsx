import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Button, Input, VStack, Text, HStack, Flex, Spinner, useToast } from '@chakra-ui/react';
import { docassist } from '../../../api/api';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import { doc, getDoc, collection, query, orderBy, getDocs, limit } from 'firebase/firestore';
import ReactMarkdown from 'react-markdown';
import Select, { components } from 'react-select'; // Import react-select and components
import { useApplicantContext } from '../../../context/ApplicantContext';

const customStyles = {
    control: (provided, state) => ({
        ...provided,
        backgroundColor: '#2d3748', // Dark background
        borderColor: state.isFocused ? '#63b3ed' : '#4a5568', // Focused state has a border color change
        color: 'white',
        cursor: 'pointer', // Make the entire control clickable
    }),
    menu: (provided) => ({
        ...provided,
        backgroundColor: '#2d3748', // Dark menu background
    }),
    option: (provided, state) => ({
        ...provided,
        backgroundColor: state.isFocused ? '#4a5568' : '#2d3748',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    }),
    multiValue: (provided) => ({
        ...provided,
        display: 'none', // Hide the selected values from appearing in the control
    }),
    placeholder: (provided) => ({
        ...provided,
        color: '#a0aec0',
    }),
    dropdownIndicator: (provided) => ({
        ...provided,
        color: 'white',
    }),
    indicatorSeparator: () => ({
        display: 'none',
    }),
};

// Custom Option component to show tick marks
const CustomOption = (props) => {
    return (
        <components.Option {...props}>
            {props.label}
            {props.isSelected ? (
                <span style={{ marginLeft: 'auto', color: 'green' }}>✔</span> // Tick mark for selected items
            ) : null}
        </components.Option>
    );
};

// Custom ValueContainer to display custom text
const CustomValueContainer = ({ children, ...props }) => {
    const { getValue, hasValue } = props;
    const selected = getValue();
    let displayText = props.selectProps.placeholder;
    if (hasValue && selected.length > 0) {
        displayText = "View Selection";
    }

    return (
        <components.ValueContainer {...props}>
            <Text color="white">{displayText}</Text>
        </components.ValueContainer>
    );
};

const DocAssist = ({ }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [selectedTags, setSelectedTags] = useState([]);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [vectorizedFiles, setVectorizedFiles] = useState([]);
    const [tags, setTags] = useState([]); // Store fetched tags here
    const toast = useToast();
    const [user] = useAuthState(auth);
    const messagesEndRef = useRef(null);
    const { selectedApplicant } = useApplicantContext();

    // Refs to track dropdown components
    const tagDropdownRef = useRef(null);
    const fileDropdownRef = useRef(null);

    // Disable file dropdown if tag is selected, and vice versa
    const isBucketDisabled = selectedFiles.length > 0;
    const isFileDisabled = selectedTags.length > 0;

    // Fetch vectorized files from Firestore
    const fetchVectorizedFiles = useCallback(async () => {
        if (user && selectedApplicant) {
            const docRef = doc(db, "applicants", selectedApplicant.id);
            const docSnap = await getDoc(docRef);
            if (docSnap.exists()) {
                setVectorizedFiles(docSnap.data().vectorized_files || []);
            } else {
                console.error("No document found for the selected applicant.");
            }
        }
    }, [user, selectedApplicant]);

    useEffect(() => {
        fetchVectorizedFiles();
    }, [fetchVectorizedFiles]);

    // Fetch chat memory (sorted by timestamp)
    // Fetch chat memory (sorted by timestamp)
    const fetchMemory = useCallback(async () => {
        if (user && selectedApplicant) {
            const memoryRef = collection(db, "chat_memory", user.uid, selectedApplicant.id);
            const q = query(memoryRef, orderBy("date_created", "desc"), limit(1));  // Get the latest document
            const querySnapshot = await getDocs(q);

            if (!querySnapshot.empty) {
                const latestDoc = querySnapshot.docs[0];  // Get the latest document
                const data = latestDoc.data();
                let history = data.history || [];  // Access the history field

                // Sort the history by timestamp in ascending order
                history = history.sort((a, b) => a.timestamp.toMillis() - b.timestamp.toMillis());

                // Extract user and assistant messages from sorted history
                const allMessages = history.flatMap(entry => [
                    { text: entry.user_message, sender: 'user' },
                    { text: entry.assistant_response, sender: 'bot' }
                ]);

                setMessages(allMessages);
            } else {
                console.error("No chat history found for the selected applicant.");
            }
        }
    }, [user, selectedApplicant]);


    useEffect(() => {
        fetchMemory(); // Load memory on component mount
    }, [fetchMemory]);

    // Scroll to the bottom whenever messages are updated
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

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

        // Temporarily display the user's question
        const tempQuestion = { text: inputMessage, sender: 'user' };
        setMessages((prevMessages) => [...prevMessages, tempQuestion]);
        setInputMessage('');
        setIsStreaming(true);

        try {
            await docassist(user.uid, selectedApplicant.id, inputMessage);

            // Fetch the full updated chat history, which includes the latest question and answer
            await fetchMemory();
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

    // Fetch customTags from Firestore
    const fetchTags = useCallback(async () => {
        if (user && selectedApplicant) {
            const docRef = doc(db, "applicants", selectedApplicant.id);
            const docSnap = await getDoc(docRef);
            if (docSnap.exists()) {
                const customTags = docSnap.data().customTags || []; // Fetch customTags
                // Map the customTags to the required format
                const mappedTags = customTags.map(tag => ({
                    label: tag,
                    value: tag.toLowerCase() // Lowercase for value
                }));
                setTags(mappedTags);
            } else {
                console.error("No document found for the selected applicant.");
            }
        }
    }, [user, selectedApplicant]);

    useEffect(() => {
        fetchTags(selectedApplicant); // Fetch tags on component mount or when user/selectedApplicant changes
    }, [fetchTags]);

    // Function to close dropdown without clearing selection
    const handleClickOutside = useCallback((e) => {
        if (
            tagDropdownRef.current && !tagDropdownRef.current.contains(e.target) &&
            fileDropdownRef.current && !fileDropdownRef.current.contains(e.target)
        ) {
            document.activeElement.blur(); // Close the dropdown
        }
    }, []);

    useEffect(() => {
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [handleClickOutside]);

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !isStreaming) {
            handleSendMessage();
        }
    };

    const clearSelections = () => {
        setSelectedTags([]);
        setSelectedFiles([]);
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
                {/* Anchor to scroll to the bottom */}
                <div ref={messagesEndRef} />
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

                    {/* Multi-Select Tag Dropdown */}
                    <Box width="200px" ref={tagDropdownRef}>
                        <Select
                            isMulti
                            options={tags}
                            value={selectedTags}
                            onChange={setSelectedTags}
                            styles={customStyles}
                            components={{
                                Option: CustomOption,
                                ValueContainer: CustomValueContainer,
                            }}
                            placeholder="Select Tags"
                            hideSelectedOptions={false}
                            closeMenuOnSelect={false}
                            menuPlacement="top"
                            isDisabled={isBucketDisabled || isStreaming}
                        />
                    </Box>

                    {/* Multi-Select File Dropdown */}
                    <Box width="200px" ref={fileDropdownRef}>
                        <Select
                            isMulti
                            options={vectorizedFiles.map(file => ({ label: file, value: file }))}
                            value={selectedFiles}
                            onChange={setSelectedFiles}
                            styles={customStyles}
                            components={{
                                Option: CustomOption,
                                ValueContainer: CustomValueContainer,
                            }}
                            placeholder="Select Files"
                            hideSelectedOptions={false}
                            closeMenuOnSelect={false}
                            menuPlacement="top"
                            isDisabled={isFileDisabled || isStreaming}
                        />
                    </Box>

                    {/* Clear Selections Button */}
                    <Button onClick={clearSelections} isDisabled={isStreaming}>
                        Clear Selections
                    </Button>

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