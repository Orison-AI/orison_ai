// ./src/api/api.js

export const processScholarLink = async (attorneyId, applicantId, scholarLink) => {
    const response = await fetch('https://e8a524ae-2fa5-4447-b6b7-6c79a0bda346.mock.pstmn.io/process-scholar-link', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        attorneyId,
        applicantId,
        scholarLink,
      }),
    });
  
    if (!response.ok) {
      throw new Error('Failed to process Google Scholar link');
    }
  
    return response.json();
  };
  