// ./src/api/api.js

// Firebase
import { functions } from '../common/firebaseConfig';
import { httpsCallable } from "firebase/functions";

// Postman mock server
// const serverUrl = "https://0ce3b64f-175d-4856-abcf-073461b968bf.mock.pstmn.io";

// Google cloud function
const serverUrl = "https://us-central1-orison-ai-visa-apply.cloudfunctions.net";

// Map function names to their endpoints
const endpoints = {
  gateway: "gateway_function_test",
  processScholarLink: "process-scholar-link",
  vectorizeFiles: "vectorize-files",
  summarize: "summarize",
}


const gateway = async (orRequestType, orRequestPayload) => {
  console.log(`Fetching: ${serverUrl}/${endpoints.gateway}, orRequestType=${orRequestType}`);

  const gatewayFunction = httpsCallable(functions, endpoints.gateway);
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

export const vectorizeFiles = async (attorneyId, applicantId, fileIds) => {
  const response = await gateway(endpoints.vectorizeFiles, {
    attorneyId,
    applicantId,
    fileIds,
  });

  console.log(`DEBUG: vectorizeFiles: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start file vectorization');
  }

  return response.data;
};

export const summarize = async (attorneyId, applicantId) => {
  const response = await gateway(endpoints.summarize, {
    attorneyId,
    applicantId,
  });

  console.log(`DEBUG: summarize: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start summarization');
  }

  return response.data;
};
