classDiagram
class UserInterface {
        +fetchUserData()
    + submitForm(data)
    }

class APILayer {
        +getUserData(userId)
    + postFormData(formData)
    }

class BackendServer {
        +queryDatabase(query)
    + insertData(data)
    }

class Database {
        +select(query)
    + insert(data)
    }

UserInterface-- > APILayer: Uses
APILayer-- > BackendServer: Calls
BackendServer-- > Database: Accesses
