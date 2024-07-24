// ./utils/deleteFolder.js
import { ref, listAll, deleteObject, getStorage } from "firebase/storage";

const deleteFolder = async (folderPath) => {
    try {
        const storage = getStorage();
        const folderRef = ref(storage, folderPath);
        const listResult = await listAll(folderRef);

        const deletePromises = listResult.items.map((itemRef) => deleteObject(itemRef));

        // Wait for all delete operations to complete
        await Promise.all(deletePromises);

        console.log(`All files in ${folderPath} have been deleted.`);
    } catch (error) {
        console.error("Error deleting folder:", error);
        throw error;
    }
};

export default deleteFolder;
