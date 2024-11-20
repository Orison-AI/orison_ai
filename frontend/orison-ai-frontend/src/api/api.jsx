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
  evidence: "evidence",
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

export const vectorizeFiles = async (attorneyId, applicantId, tag, fileId) => {
  const response = await gateway(endpoints.vectorizeFiles, {
    attorneyId,
    applicantId,
    tag,
    fileId,
  });

  console.log(`INFO: vectorizeFiles: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start file vectorization');
  }

  return response.data;
};

export const deleteFileVectors = async (attorneyId, applicantId, tag, fileId) => {
  const response = await gateway(endpoints.deleteFileVectors, {
    attorneyId,
    applicantId,
    tag,
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

export const evidence = async (attorneyId, applicantId) => {
  const response = await gateway(endpoints.evidence, {
    attorneyId,
    applicantId,
  });

  console.log(`INFO: evidence: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start evidence');
  }

  return response.data;
};

export const docassist = async (attorneyId, applicantId, message, tag, filename) => {
  const response = await gateway(endpoints.docassist, {
    attorneyId,
    applicantId,
    message,
    tag,
    filename
  });

  console.log(`INFO: docassist: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start docassist');
  }

  return response.data;
};
