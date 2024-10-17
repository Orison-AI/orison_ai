// ./src/api/api.js

// Firebase
import { functions } from '../common/firebaseConfig';
import { httpsCallable } from "firebase/functions";

// Map function names to their endpoints
const endpoints = {
  gateway: "gateway_function",
  processScholarLink: "process-scholar-link",
  processScholarNetwork: "process-scholar-network",
  vectorizeFiles: "vectorize-files",
  summarize: "summarize",
  deleteFileVectors: "delete-file-vectors",
  docassist: "docassist",
}

// Default timeout 5 minutes * 60 seconds/minute * 1000 milliseconds/second
const gateway = async (orRequestType, orRequestPayload, timeout = 5 * 60 * 1000) => {
  console.log(`Fetching cloud endpoint: ${endpoints.gateway}, orRequestType=${orRequestType}`);

  const options = {
    timeout,
  };

  const gatewayFunction = httpsCallable(functions, endpoints.gateway, options);
  try {
    return await gatewayFunction({
      "or_request_type": orRequestType,
      "or_request_payload": orRequestPayload,
    });
  } catch (error) {
    console.error(`ERROR: gatewayFunction: code=${error.code}, message=${error.message}`);
    return {
      data: null,
      code: error.code || 500,
      message: error.message,
    };
  }
};

export const processScholarLink = async (attorneyId, applicantId, scholarLink) => {
  const response = await gateway(endpoints.processScholarLink, {
    attorneyId,
    applicantId,
    scholarLink,
  });

  console.log(`INFO: processScholarLink: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to process Google Scholar link');
  }

  return response.data;
};

export const processScholarNetwork = async (attorneyId, applicantId, scholarLink) => {
  const response = await gateway(endpoints.processScholarNetwork, {
    attorneyId,
    applicantId,
    scholarLink,
  });

  console.log(`INFO: processScholarNetwork: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to process Google Scholar Network');
  }

  return response.data;
};

export const vectorizeFiles = async (attorneyId, applicantId, bucket, fileId) => {
  const response = await gateway(endpoints.vectorizeFiles, {
    attorneyId,
    applicantId,
    bucket,
    fileId,
  });

  console.log(`INFO: vectorizeFiles: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start file vectorization');
  }

  return response.data;
};

export const deleteFileVectors = async (attorneyId, applicantId, bucket, fileId) => {
  const response = await gateway(endpoints.deleteFileVectors, {
    attorneyId,
    applicantId,
    bucket,
    fileId,
  });

  console.log(`INFO: deleteFileVectors: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to delete file vectors');
  }

  return response.data;
};

export const summarize = async (attorneyId, applicantId) => {
  const response = await gateway(endpoints.summarize, {
    attorneyId,
    applicantId,
  });

  console.log(`INFO: summarize: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start summarization');
  }

  return response.data;
};

// New SSE connection function for DocAssist
export const docassist = (attorneyId, applicantId, message, onChunkReceived, onComplete, onError, onStop) => {
  const url = `${endpoints.docassist}?attorneyId=${encodeURIComponent(attorneyId)}&applicantId=${encodeURIComponent(applicantId)}&message=${encodeURIComponent(message)}`;

  // Create a Server-Sent Events connection
  const eventSource = new EventSource(url);

  // Triggered when a new chunk of data is received
  eventSource.onmessage = function (event) {
    const dataChunk = event.data;
    onChunkReceived(dataChunk); // Pass chunk to UI to display
  };

  // Triggered when the server completes the event stream
  eventSource.addEventListener('complete', function () {
    eventSource.close(); // Close the connection when complete
    onComplete(); // Notify UI
  });

  // Handle errors from the SSE connection
  eventSource.onerror = function (error) {
    console.error('SSE error:', error);
    onError(error); // Notify UI about error
    eventSource.close(); // Close connection on error
  };

  // Function to stop the event stream manually
  const stopStream = () => {
    eventSource.close();
    onStop(); // Trigger stop callback
  };

  return stopStream; // Return stop function
};

