```mermaid
classDiagram
class UserInterface {
        +process_scholar(scholar_link)
        +display_informatics(scholar_data)
    }

class HTTPLayer {
        +fetch_scholar(attorney_id, applicant_id, scholar_link)
        +get_scholar_data(attorney_id, applicant_id, field)
    }

class BackendServer {
        +fetch_scholar(attorney_id, applicant_id, scholar_link)
        +queryDatabase(query)
        +insertData(data)
    }

class Database {
        +select(query)
        +insert(data)
    }

UserInterface-- > HTTPLayer: Uses
HTTPLayer-- > BackendServer: Calls
BackendServer-- > Database: Accesses
Database --> BackendServer: Returns data
BackendServer --> HTTPLayer: Sends response
HTTPLayer --> UserInterface: Returns data
```