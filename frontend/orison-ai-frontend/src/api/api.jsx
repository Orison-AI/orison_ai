// ./src/api/api.js

import { httpsCallable } from 'firebase/functions';
import { functions } from '../common/firebaseConfig';

// Check if we should use local testing
const USE_LOCAL = process.env.REACT_APP_LOCAL_TEST === 'true';
const LOCAL_API_BASE_URL = 'http://localhost:5004';

// Firebase Functions gateway call
const firebaseGatewayCall = async (orRequestType, orRequestPayload, timeout = 5 * 60 * 1000) => {
  const gatewayFunction = httpsCallable(functions, 'gateway_function');
  
  try {
    const result = await gatewayFunction({
      or_request_type: orRequestType,
      or_request_payload: orRequestPayload,
    });
    
    return result.data;
  } catch (error) {
    console.error('Firebase Functions error:', error);
    throw error;
  }
};

// Local gateway call (existing implementation)
const localGatewayCall = async (orRequestType, orRequestPayload, timeout = 5 * 60 * 1000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(`${LOCAL_API_BASE_URL}/gateway_function`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        or_request_type: orRequestType,
        or_request_payload: orRequestPayload,
      }),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

// Conditional gateway call - uses Firebase by default, localhost when LOCAL_TEST is set
const gatewayCall = async (orRequestType, orRequestPayload, timeout = 5 * 60 * 1000) => {
  if (USE_LOCAL) {
    console.log('INFO: Using local gateway at localhost:5004');
    return await localGatewayCall(orRequestType, orRequestPayload, timeout);
  } else {
    console.log('INFO: Using Firebase Functions gateway');
    return await firebaseGatewayCall(orRequestType, orRequestPayload, timeout);
  }
};

export const processScholarLink = async (attorneyId, applicantId, scholarLink) => {
  // Use longer timeout for Google Scholar operations (15 minutes)
  const response = await gatewayCall('process-scholar-link', {
    attorneyId,
    applicantId,
    scholarLink,
  }, 15 * 60 * 1000); // 15 minutes

  console.log(`INFO: processScholarLink: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to process Google Scholar link');
  }

  return response.data;
};

export const processScholarNetwork = async (attorneyId, applicantId, scholarLink, maxDepth = 3, maxSize = 100) => {
  // Use much longer timeout for network building (30 minutes)
  const response = await gatewayCall('process-scholar-network', {
    attorneyId,
    applicantId,
    scholarLink,
    max_depth: maxDepth,
    max_size: maxSize,
  }, 30 * 60 * 1000); // 30 minutes

  console.log(`INFO: processScholarNetwork: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to process Google Scholar Network');
  }

  return response.data;
};

export const vectorizeFiles = async (attorneyId, applicantId, tag, fileId) => {
  const response = await gatewayCall('vectorize-files', {
    attorneyId,
    applicantId,
    tag: [tag], // Convert to array as expected by backend
    fileId,
  });

  console.log(`INFO: vectorizeFiles: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to start file vectorization');
  }

  return response.data;
};

export const deleteFileVectors = async (attorneyId, applicantId, tag, fileId) => {
  const response = await gatewayCall('delete-file-vectors', {
    attorneyId,
    applicantId,
    tag,
    fileId,
  });

  console.log(`INFO: deleteFileVectors: response=${JSON.stringify(response)}`);

  if (!response.data) {
    throw new Error('Failed to delete file vectors');
  }

  // Check if the operation was successful
  if (response.data.message && response.data.message.includes('successfully')) {
    return response.data;
  } else {
    throw new Error(response.data.message || 'Failed to delete file vectors');
  }
};

export const summarize = async (attorneyId, applicantId) => {
  const response = await gatewayCall('summarize', {
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
  const response = await gatewayCall('evidence', {
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
  const response = await gatewayCall('docassist', {
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
