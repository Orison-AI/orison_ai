import { doc, getDoc, getDocs, setDoc, updateDoc, collection } from "firebase/firestore";
import { auth, db } from "../../../common/firebaseConfig";

export const fetchTags = async (selectedApplicant) => {
    try {
        // Reference the applicant's document in Firestore
        const applicantDocRef = doc(db, "applicants", selectedApplicant.id);

        // Fetch the document
        const applicantDoc = await getDoc(applicantDocRef);

        if (applicantDoc.exists()) {
            const data = applicantDoc.data();
            return data.customTags || []; // Return the customTags field or an empty array if it doesn't exist
        } else {
            console.error("Applicant document does not exist.");
            return [];
        }
    } catch (error) {
        console.error("Error fetching custom tags:", error);
        return [];
    }
};


export const fetchQuestionnaire = async (applicantId) => {
    try {
        const user = auth.currentUser;
        if (!user) throw new Error("User not authenticated");

        const questionnaireDocRef = doc(db, "templates", applicantId);
        const questionnaireDoc = await getDoc(questionnaireDocRef);

        if (questionnaireDoc.exists()) {
            const questionnaireData = questionnaireDoc.data();
            const taskArray = questionnaireData.task || [];
            const questions = taskArray.map((taskItem, index) => ({
                id: index + 1,
                text: taskItem.question,
                tag: taskItem.tag || [], // Tags are a list
                detail_level: taskItem.detail_level || "",
                isEditing: false,
            }));
            return { questions, exists: true };
        }
        return { questions: [], exists: false };
    } catch (error) {
        console.error("Error fetching questionnaire:", error);
        return { questions: [], exists: false };
    }
};

export const handleTagChange = async (applicantId, questionId, updatedTags, questions, setQuestions) => {
    try {
        const updatedQuestions = questions.map((question) =>
            question.id === questionId ? { ...question, tag: updatedTags } : question
        );

        setQuestions(updatedQuestions);

        const questionnaireDocRef = doc(db, "templates", applicantId);
        await updateDoc(questionnaireDocRef, {
            task: updatedQuestions.map(({ id, text, tag, detail_level }) => ({
                question: text,
                tag,
                detail_level,
            })),
        });
    } catch (error) {
        console.error("Error updating tags in Firestore:", error);
    }
};

export const updateQuestion = async (applicantId, id, text, tag, detail_level, questions, setQuestions) => {
    const updatedQuestions = questions.map((q) =>
        q.id === id ? { ...q, text, tag, detail_level, isEditing: false } : q
    );
    setQuestions(updatedQuestions);

    const questionnaireDocRef = doc(db, "templates", applicantId);
    await updateDoc(questionnaireDocRef, {
        task: updatedQuestions.map(({ id, text, tag, detail_level }) => ({
            question: text,
            tag,
            detail_level,
        })),
    });
};

export const editQuestion = (id, questions, setQuestions) => {
    setQuestions(questions.map((q) => (q.id === id ? { ...q, isEditing: true } : q)));
};

export const deleteQuestion = async (applicantId, id, questions, setQuestions) => {
    const updatedQuestions = questions.filter((q) => q.id !== id);
    setQuestions(updatedQuestions);

    const questionnaireDocRef = doc(db, "templates", applicantId);
    await updateDoc(questionnaireDocRef, {
        task: updatedQuestions.map(({ id, text, tag, detail_level }) => ({
            question: text,
            tag,
            detail_level,
        })),
    });
};

export const addQuestion = (setIdCounter, questions, setQuestions) => {
    const newQuestion = {
        id: questions.length + 1,
        text: "",
        tag: [],
        detail_level: "",
        isEditing: true,
    };

    const updatedQuestions = [...questions, newQuestion];
    setQuestions(updatedQuestions);
    setIdCounter((prev) => prev + 1);
};

export const createFromTemplate = async (selectedApplicant, setQuestions, setDocumentExists) => {
    let templateFileName;
    switch (selectedApplicant.visaCategory) {
        case "EB1":
            templateFileName = "eb1_a_questionnaire";
            break;
        case "O1":
            templateFileName = "eb1_a_questionnaire";
            break;
        case "EB2":
            templateFileName = "eb1_a_questionnaire";
            break;
        default:
            templateFileName = "eb1_a_questionnaire";
    }

    try {
        const templateDocRef = doc(db, "templates", templateFileName);
        const templateDoc = await getDoc(templateDocRef);

        if (templateDoc.exists()) {
            const templateData = templateDoc.data();
            const templateTasks = templateData.task || [];

            const questionnaireDocRef = doc(db, "templates", selectedApplicant.id);
            const userDocSnapshot = await getDoc(questionnaireDocRef);

            let updatedTaskArray;
            if (userDocSnapshot.exists()) {
                const existingData = userDocSnapshot.data();
                const existingTasks = existingData.task || [];
                updatedTaskArray = [...existingTasks, ...templateTasks];
            } else {
                updatedTaskArray = templateTasks;
            }

            await setDoc(questionnaireDocRef, { task: updatedTaskArray }, { merge: true });

            const extractedQuestions = updatedTaskArray.map((taskItem, index) => ({
                id: index + 1,
                text: taskItem.question,
                tag: taskItem.tag || [],
                detail_level: taskItem.detail_level || "",
                isEditing: false,
            }));

            setQuestions(extractedQuestions);
            setDocumentExists(true);
        }
    } catch (error) {
        console.error("Error creating questionnaire from template:", error);
    }
};

export const deleteAllQuestions = async (applicantId) => {
    try {
        const questionnaireDocRef = doc(db, "templates", applicantId);
        await updateDoc(questionnaireDocRef, { task: [] }); // Clear the task array
        console.log("All questions deleted successfully.");
    } catch (error) {
        console.error("Error deleting all questions:", error);
        throw error; // Propagate the error for handling in the caller
    }
};