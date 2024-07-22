// ./utils/copyFile.js
import { ref, getDownloadURL, uploadBytesResumable, getStorage } from "firebase/storage";

const copyFile = async (sourcePath, destinationPath) => {
    try {
        const storage = getStorage();

        // Reference to the source file
        const sourceRef = ref(storage, sourcePath);

        // Get the download URL for the source file
        const downloadURL = await getDownloadURL(sourceRef);

        // Fetch the file from the download URL
        const response = await fetch(downloadURL);
        const fileBlob = await response.blob();

        // Reference to the destination file
        const destinationRef = ref(storage, destinationPath);

        // Upload the file to the destination path
        const uploadTask = uploadBytesResumable(destinationRef, fileBlob);

        return new Promise((resolve, reject) => {
            uploadTask.on(
                "state_changed",
                null,
                (error) => {
                    reject(error);
                },
                () => {
                    resolve(uploadTask.snapshot);
                }
            );
        });
    } catch (error) {
        console.error("Error copying file:", error);
        throw error;
    }
};

export default copyFile;
