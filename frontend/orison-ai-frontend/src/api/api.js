// ./src/api/api.js

// Firebase
// import { auth } from '../common/firebaseConfig';
import { functions } from '../common/firebaseConfig';
import { httpsCallable } from "firebase/functions";


// Postman mock server
// const serverUrl = "https://0ce3b64f-175d-4856-abcf-073461b968bf.mock.pstmn.io";

// Google cloud function
// const serverUrl = "https://us-central1-orison-ai-visa-apply.cloudfunctions.net";

// Map function names to their endpoints
const endpoints = {
  gateway: "gateway_function",
  processScholarLink: "process-scholar-link",
  vectorizeFiles: "vectorize-files",
  summarize: "summarize",
}

const gateway = async (orRequestType, orRequestPayload) => {
  // const user = auth.currentUser;
  // if (!user) {
  //   throw new Error('User not authenticated');
  // }

  // const idToken = await user.getIdToken();

  // return await fetch(`${serverUrl}/${endpoints.gateway}`, {
  //   method: 'POST',
  //   headers: {
  //     'Content-Type': 'application/json',
  //     'Authorization': `Bearer ${idToken}`,
  //   },
  //   body: JSON.stringify({
  //     "or_request_type": orRequestType,
  //     "or_request_payload": orRequestPayload,
  //   }),
  // });

  const gatewayFunction = httpsCallable(functions, endpoints.gateway);
  gatewayFunction({
    "or_request_type": orRequestType,
    "or_request_payload": orRequestPayload,
  })
  .then((result) => {
    const data = result.data;
    console.log(`DEBUG: data=${data}`);
    const sanitizedMessage = data.text;
    console.log(`DEBUG: sanitizedMessage=${sanitizedMessage}`);
  })
  .catch((error) => {
    console.error(`ERROR: error.code=${error.code}`);
    console.error(`ERROR: error.message=${error.message}`);
    console.error(`ERROR: error.details=${error.details}`);
  });
};

export const processScholarLink = async (attorneyId, applicantId, scholarLink) => {
  const response = await gateway(endpoints.processScholarLink, {
    attorneyId,
    applicantId,
    scholarLink,
  });

  if (!response.ok) {
    throw new Error('Failed to process Google Scholar link');
  }

  return response.json();
};

export const vectorizeFiles = async (attorneyId, applicantId, fileIds) => {
  const response = await gateway(endpoints.vectorizeFiles, {
    attorneyId,
    applicantId,
    fileIds,
  });

  if (!response.ok) {
    throw new Error('Failed to start file vectorization');
  }

  return response.json();
};

export const summarize = async (attorneyId, applicantId) => {
  const response = await gateway(endpoints.summarize, {
    attorneyId,
    applicantId,
  });

  if (!response.ok) {
    throw new Error('Failed to start summarization');
  }

  return response.json();
};
