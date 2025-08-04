// ./components/pages/ApplicantDocuments/ScholarData/ScholarDataModal.jsx

// React
import React from 'react';

// Chakra UI
import {
  Box, Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalBody, ModalFooter, Button, Text, VStack, HStack,
  Badge, Divider, Heading, SimpleGrid, Stat, StatLabel, StatNumber,
  Table, Thead, Tbody, Tr, Th, Td, TableContainer, Card, CardBody,
  CardHeader, Flex, Icon, Link, Tooltip, Wrap, WrapItem,
  Accordion, AccordionItem, AccordionButton, AccordionPanel,
  AccordionIcon, List, ListItem, ListIcon, Progress,
} from '@chakra-ui/react';

// Icons
import { 
  FaGraduationCap, FaUniversity, FaEnvelope, FaExternalLinkAlt,
  FaUsers, FaBook, FaChartLine, FaStar, FaGlobe, FaCalendar,
  FaQuoteLeft, FaCheckCircle, FaUser
} from 'react-icons/fa';

const ScholarDataModal = ({ isOpen, onClose, data }) => {
  // Handle missing or null data
  if (!data) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} size="3xl">
        <ModalOverlay />
        <ModalContent p="20px">
          <ModalHeader fontSize="2xl">Scholar Data</ModalHeader>
          <ModalBody>
            <Box bg="gray.900" p="20px" borderRadius="8px">
              <Text color="gray.400">No scholar data available</Text>
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    );
  }

  // Extract and format data from the actual backend structure
  const author = data.author || {};
  const coAuthors = data.co_authors || [];
  const publications = data.publications || [];
  const network = data.network || [];
  const keywords = data.keywords || [];
  const citedBy = data.cited_by || 0;
  const hIndex = data.h_index || 0;
  const citedBy5y = data.cited_by_5y || 0;
  const hIndex5y = data.h_index_5y || 0;

  // Sort publications by citations (descending)
  const sortedPublications = [...publications].sort((a, b) => (b.cited_by || 0) - (a.cited_by || 0));
  
  // Sort network by citations (descending)
  const sortedNetwork = [...network].sort((a, b) => (b.citations || 0) - (a.citations || 0));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent p="20px" maxH="90vh">
        <ModalHeader fontSize="2xl">
          <VStack align="start" spacing={2}>
            <HStack>
              <Icon as={FaGraduationCap} color="blue.400" />
              <Text>Scholar Profile</Text>
            </HStack>
            {author.name && (
              <Text fontSize="lg" color="gray.400" fontWeight="normal">
                {author.name}
              </Text>
            )}
          </VStack>
        </ModalHeader>
        
        <ModalBody>
          <VStack spacing={6} align="stretch">
            
            {/* Research Metrics Summary */}
            <Card bg="gray.800" border="1px solid" borderColor="gray.700">
              <CardHeader>
                <HStack>
                  <Icon as={FaChartLine} color="blue.400" />
                  <Heading size="md">Research Impact Metrics</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
                  <Stat>
                    <StatLabel color="gray.400" fontSize="sm">Total Citations</StatLabel>
                    <StatNumber color="blue.400" fontSize="2xl">
                      {citedBy.toLocaleString()}
                    </StatNumber>
                    {citedBy5y > 0 && (
                      <Text fontSize="xs" color="gray.500">
                        {citedBy5y.toLocaleString()} (5-year)
                      </Text>
                    )}
                  </Stat>
                  <Stat>
                    <StatLabel color="gray.400" fontSize="sm">H-Index</StatLabel>
                    <StatNumber color="green.400" fontSize="2xl">
                      {hIndex}
                    </StatNumber>
                    {hIndex5y > 0 && (
                      <Text fontSize="xs" color="gray.500">
                        {hIndex5y} (5-year)
                      </Text>
                    )}
                  </Stat>
                  <Stat>
                    <StatLabel color="gray.400" fontSize="sm">Publications</StatLabel>
                    <StatNumber color="purple.400" fontSize="2xl">
                      {publications.length}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel color="gray.400" fontSize="sm">Research Network</StatLabel>
                    <StatNumber color="orange.400" fontSize="2xl">
                      {network.length}
                    </StatNumber>
                  </Stat>
                </SimpleGrid>
              </CardBody>
            </Card>

            {/* Author Information */}
            <Card bg="gray.800" border="1px solid" borderColor="gray.700">
              <CardHeader>
                <HStack>
                  <Icon as={FaUser} color="green.400" />
                  <Heading size="md">Author Information</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <VStack align="start" spacing={3}>
                    <HStack>
                      <Icon as={FaUniversity} color="gray.400" />
                      <Text color="gray.300">
                        <strong>Affiliation:</strong> {author.affiliation || 'Not specified'}
                      </Text>
                    </HStack>
                    <HStack>
                      <Icon as={FaEnvelope} color="gray.400" />
                      <Text color="gray.300">
                        <strong>Email:</strong> {author.email || 'Not available'}
                      </Text>
                    </HStack>
                    <HStack>
                      <Icon as={FaGlobe} color="gray.400" />
                      <Text color="gray.300">
                        <strong>Scholar ID:</strong> {author.scholar_id || 'Unknown'}
                      </Text>
                    </HStack>
                  </VStack>
                  <VStack align="start" spacing={3}>
                    {author.profile_link && (
                      <HStack>
                        <Icon as={FaExternalLinkAlt} color="gray.400" />
                        <Link href={author.profile_link} isExternal color="blue.400">
                          View Google Scholar Profile
                        </Link>
                      </HStack>
                    )}
                    {keywords.length > 0 && (
                      <VStack align="start" spacing={2}>
                        <Text color="gray.300" fontWeight="bold">Research Areas:</Text>
                        <Wrap>
                          {keywords.map((keyword, index) => (
                            <WrapItem key={index}>
                              <Badge colorScheme="blue" variant="subtle">
                                {keyword}
                              </Badge>
                            </WrapItem>
                          ))}
                        </Wrap>
                      </VStack>
                    )}
                  </VStack>
                </SimpleGrid>
              </CardBody>
            </Card>

            {/* Research Network Table */}
            {network.length > 0 && (
              <Card bg="gray.800" border="1px solid" borderColor="gray.700">
                <CardHeader>
                  <HStack>
                    <Icon as={FaUsers} color="orange.400" />
                    <Heading size="md">Research Network ({network.length} scholars)</Heading>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <TableContainer>
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th color="gray.400">Name</Th>
                          <Th color="gray.400" isNumeric>Citations</Th>
                          <Th color="gray.400" isNumeric>H-Index</Th>
                          <Th color="gray.400" isNumeric>Publications</Th>
                          <Th color="gray.400">Affiliation</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {/* Primary Scholar (from scholar database) */}
                        <Tr bg="blue.900">
                          <Td>
                            <HStack>
                              <Text fontWeight="bold" color="blue.300">
                                {author.name || 'Unknown'}
                              </Text>
                              <Badge colorScheme="blue" size="sm">Primary</Badge>
                            </HStack>
                          </Td>
                          <Td isNumeric color="blue.400" fontWeight="bold">
                            {citedBy.toLocaleString()}
                          </Td>
                          <Td isNumeric color="green.400" fontWeight="bold">
                            {hIndex}
                          </Td>
                          <Td isNumeric color="purple.400" fontWeight="bold">
                            {publications.length}
                          </Td>
                          <Td color="gray.300" fontSize="sm">
                            {author.affiliation || 'Not specified'}
                          </Td>
                        </Tr>
                        {/* Network Scholars */}
                        {sortedNetwork.map((scholar, index) => (
                          <Tr key={index} bg="transparent">
                            <Td>
                              <Text color="white">
                                {scholar.name}
                              </Text>
                            </Td>
                            <Td isNumeric color="blue.400" fontWeight="bold">
                              {scholar.citations?.toLocaleString() || 0}
                            </Td>
                            <Td isNumeric color="green.400" fontWeight="bold">
                              {scholar.h_index || 0}
                            </Td>
                            <Td isNumeric color="purple.400" fontWeight="bold">
                              {scholar.publication_count || 0}
                            </Td>
                            <Td color="gray.300" fontSize="sm">
                              {scholar.affiliation || 'Not specified'}
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TableContainer>
                </CardBody>
              </Card>
            )}

            {/* Publications */}
            {publications.length > 0 && (
              <Card bg="gray.800" border="1px solid" borderColor="gray.700">
                <CardHeader>
                  <HStack>
                    <Icon as={FaBook} color="purple.400" />
                    <Heading size="md">Publications ({publications.length})</Heading>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <Accordion allowMultiple>
                    {sortedPublications.slice(0, 10).map((pub, index) => (
                      <AccordionItem key={index} border="none" mb={2}>
                        <AccordionButton 
                          bg="gray.700" 
                          _hover={{ bg: "gray.600" }}
                          borderRadius="md"
                        >
                          <Box flex="1" textAlign="left">
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="bold" color="white" fontSize="sm">
                                {pub.title}
                              </Text>
                              <HStack spacing={4} fontSize="xs" color="gray.400">
                                <Text>{pub.authors}</Text>
                                <Text>•</Text>
                                <Text>{pub.year}</Text>
                                <Text>•</Text>
                                <Text>{pub.cited_by || 0} citations</Text>
                              </HStack>
                            </VStack>
                          </Box>
                          <AccordionIcon color="gray.400" />
                        </AccordionButton>
                        <AccordionPanel bg="gray.750" borderRadius="md" mt={1}>
                          <VStack align="start" spacing={2}>
                            {pub.abstract && (
                              <Box>
                                <Text fontSize="xs" color="gray.400" fontWeight="bold">Abstract:</Text>
                                <Text fontSize="sm" color="gray.300" fontStyle="italic">
                                  <Icon as={FaQuoteLeft} mr={2} color="gray.500" />
                                  {pub.abstract}
                                </Text>
                              </Box>
                            )}
                            <HStack spacing={4} fontSize="xs">
                              <Badge colorScheme="blue" variant="subtle">
                                {pub.type_of_paper || 'Unknown Type'}
                              </Badge>
                              <Text color="gray.400">
                                <strong>Journal:</strong> {pub.forum_name || pub.peer_reviews || 'Unknown'}
                              </Text>
                            </HStack>
                          </VStack>
                        </AccordionPanel>
                      </AccordionItem>
                    ))}
                  </Accordion>
                  {publications.length > 10 && (
                    <Text color="gray.500" fontSize="sm" mt={4} textAlign="center">
                      Showing top 10 publications by citations. Total: {publications.length}
                    </Text>
                  )}
                </CardBody>
              </Card>
            )}

            {/* Co-authors */}
            {coAuthors.length > 0 && (
              <Card bg="gray.800" border="1px solid" borderColor="gray.700">
                <CardHeader>
                  <HStack>
                    <Icon as={FaUsers} color="teal.400" />
                    <Heading size="md">Co-authors ({coAuthors.length})</Heading>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                    {coAuthors.map((coauthor, index) => (
                      <Box 
                        key={index} 
                        p={3} 
                        bg="gray.700" 
                        borderRadius="md"
                        border="1px solid"
                        borderColor="gray.600"
                      >
                        <VStack align="start" spacing={2}>
                          <Text fontWeight="bold" color="white">
                            {coauthor.name}
                          </Text>
                          <Text fontSize="sm" color="gray.400">
                            {coauthor.affiliation || 'Affiliation not specified'}
                          </Text>
                          {coauthor.profile_link && (
                            <Link href={coauthor.profile_link} isExternal color="blue.400" fontSize="xs">
                              <HStack>
                                <Icon as={FaExternalLinkAlt} />
                                <Text>View Profile</Text>
                              </HStack>
                            </Link>
                          )}
                        </VStack>
                      </Box>
                    ))}
                  </SimpleGrid>
                </CardBody>
              </Card>
            )}

          </VStack>
        </ModalBody>
        
        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ScholarDataModal;
