import React, { useCallback, useEffect, useState } from 'react';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth, db } from '../../../common/firebaseConfig';
import {
  collection, getDocs, orderBy, query, limit, doc,
} from 'firebase/firestore';
import {
  Box, Button, Center, HStack, Text, useToast, VStack, Spinner,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';
import { summarize } from '../../../api/api';
import SummarizationDataDisplay from './SummarizationDataDisplay';
import { useApplicantContext } from '../../../context/ApplicantContext';
import { jsPDF } from 'jspdf';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const ApplicantSummarization = () => {
  const [user] = useAuthState(auth);
  const [summarizationDataStatus, setSummarizationDataStatus] = useState('');
  const [summarizationData, setSummarizationData] = useState(null);
  const [summarizationProgress, setSummarizationProgress] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const toast = useToast();
  const { selectedApplicant } = useApplicantContext();

  const fetchSummarizationData = useCallback(async () => {
    if (user && selectedApplicant) {
      setSummarizationDataStatus('loading');
      const summarizationQuery = query(
        collection(doc(collection(db, "screening_builder"), user.uid), selectedApplicant.id),
        orderBy("date_created", "desc"),
        limit(1)
      );
      const querySnapshot = await getDocs(summarizationQuery);
      if (querySnapshot.empty) {
        setSummarizationData(null);
        setSummarizationDataStatus('not_found');
        setLastUpdated('');
      } else {
        const data = querySnapshot.docs[0].data();

        if (data.date_created && typeof data.date_created.toDate === "function") {
          const timestamp = data.date_created.toDate();
          setLastUpdated(new Intl.DateTimeFormat('en-US', {
            dateStyle: 'medium',
            timeStyle: 'short',
          }).format(timestamp));
        }

        setSummarizationData(data);
        setSummarizationDataStatus('found');
      }
    }
  }, [user, selectedApplicant]);

  useEffect(() => {
    fetchSummarizationData();
  }, [fetchSummarizationData, selectedApplicant]);

  const handleSummarize = async () => {
    if (selectedApplicant) {
      try {
        setSummarizationProgress('loading');
        await summarize(user.uid, selectedApplicant.id);
        setSummarizationProgress('success');
        toast({
          title: 'Summary Complete',
          description: `Summary generated successfully for ${selectedApplicant.name}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        await fetchSummarizationData();
      } catch (error) {
        setSummarizationProgress('error');
        toast({
          title: 'Summary Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const generateHTMLContent = () => {
    if (!summarizationData || !summarizationData.summary) return '';

    let html = `
      <html>
        <head>
          <title>Summary Preview</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { font-size: 22px; color: #007acc; }
            h2 { font-size: 18px; color: #0056b3; margin-top: 20px; }
            p, ul, ol, li, pre { font-size: 16px; color: black; margin: 5px 0; }
            hr { border: 1px solid #ccc; margin: 20px 0; }
            .source { font-style: italic; color: gray; }
          </style>
        </head>
        <body>
          <h1>Summary for ${selectedApplicant.name}</h1>
          <p><strong>Last Updated:</strong> ${lastUpdated}</p>
          <hr>
    `;

    summarizationData.summary.forEach(({ question, answer, source }) => {
      const sanitizedAnswer = DOMPurify.sanitize(marked(answer));
      html += `<h2>${question}</h2>`;
      html += `<div>${sanitizedAnswer}</div>`;
      if (source) {
        html += `<p class="source">Source: ${source}</p>`;
      }
      html += `<hr>`;
    });

    html += `</body></html>`;
    return html;
  };

  const handlePreviewPDF = () => {
    if (!summarizationData || !summarizationData.summary) return;

    const newWindow = window.open("", "_blank");
    if (newWindow) {
      newWindow.document.write(generateHTMLContent());
      newWindow.document.close();
    } else {
      alert("Popup blocked! Please allow popups to preview the PDF.");
    }
  };

  const handleDownloadPDF = async () => {
    if (!summarizationData || !summarizationData.summary) return;

    const doc = new jsPDF({
      orientation: "p",
      unit: "mm",
      format: "a4",
    });

    const pdfContent = generateHTMLContent();
    const lines = pdfContent.split(/<hr>/).map(section => section.replace(/<[^>]*>?/gm, ''));

    let y = 10;
    doc.setFont("helvetica", "bold");
    doc.text(`Summary for ${selectedApplicant.name}`, 10, y);
    y += 10;

    doc.setFont("helvetica", "normal");
    lines.forEach((line) => {
      if (y > 280) {
        doc.addPage();
        y = 10;
      }
      doc.text(line, 10, y, { maxWidth: 190 });
      y += 7;
    });

    doc.save(`Summary_${selectedApplicant.name}.pdf`);
  };

  return (
    <Box className="oai-appsum" height="100%" width="100%">
      <Center width="100%" flex="1">
        <VStack height="100%" width="100%">
          <HStack mb="20px" justifyContent="flex-start">
            <Button onClick={handleSummarize} colorScheme="green" isDisabled={summarizationProgress === 'loading'}>Generate Summary</Button>
            <Button onClick={handlePreviewPDF} colorScheme="blue" isDisabled={!summarizationData}>Display PDF</Button>
            {/* <Button onClick={handleDownloadPDF} colorScheme="purple" isDisabled={!summarizationData}>Download PDF</Button> */}
          </HStack>

          {summarizationDataStatus === 'found' && <SummarizationDataDisplay data={summarizationData} />}
        </VStack>
      </Center>
    </Box>
  );
};

export default ApplicantSummarization;
