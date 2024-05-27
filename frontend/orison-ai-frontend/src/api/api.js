// ./src/api/api.js

const serverUrl = "https://0ce3b64f-175d-4856-abcf-073461b968bf.mock.pstmn.io";

// Map function names to their endpoints
const endpoints = {
  gateway: "gateway",
  processScholarLink: "process-scholar-link",
  vectorizeFiles: "vectorize-files",
  summarize: "summarize",
}

const gateway = async (orRequestType, orRequestPayload) => {
  return await fetch(`${serverUrl}/${endpoints.gateway}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "or_request_type": orRequestType,
      "or_request_payload": orRequestPayload,
    }),
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
