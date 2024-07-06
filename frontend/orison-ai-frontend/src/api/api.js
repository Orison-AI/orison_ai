// ./src/api/api.js

// Firebase
import { functions } from '../common/firebaseConfig';
import { httpsCallable } from "firebase/functions";

// Map function names to their endpoints
const endpoints = {
  gateway: "gateway_function",
  processScholarLink: "process-scholar-link",
  vectorizeFiles: "vectorize-files",
  summarize: "summarize",
  deleteFileVectors: "delete-file-vectors",
}

// Default timeout 5 minutes * 60 seconds/minute * 1000 milliseconds/second
const gateway = async (orRequestType, orRequestPayload, timeout=5 * 60 * 1000) => {
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

export const vectorizeFiles = async (attorneyId, applicantId, bucket, fileIds) => {
  const response = await gateway(endpoints.vectorizeFiles, {
    attorneyId,
    applicantId,
    bucket,
    fileIds,
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
