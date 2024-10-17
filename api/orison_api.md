graph TD
    subgraph OrisonAI API
        A[process-scholar-link]
        B[vectorize-files]
        C[summarize]
        D[process-scholar-network]
        E[delete-file-vectors]
        F[docassist]
        G[gateway]
    end

    subgraph Data Models
        H[AttorneyId]
        I[ApplicantId]
        J[RequestId]
        K[scholarLink]
        L[fileId]
        M[bucket]
        N[chatMessages]
        O[or_request_type]
        P[or_request_payload]
    end

    A --> Q{Request}
    Q --> H
    Q --> I
    Q --> K

    B --> R{Request}
    R --> H
    R --> I
    R --> M
    R --> L

    C --> S{Request}
    S --> H
    S --> I

    D --> T{Request}
    T --> H
    T --> I
    T --> K

    E --> U{Request}
    U --> H
    U --> I
    U --> M
    U --> L

    F --> V{Request}
    V --> H
    V --> I
    V --> N

    G --> W{Request}
    W --> O
    W --> P

    subgraph Responses
        X[202]
    end

    Q --> X
    R --> X
    S --> X
    T --> X
    U --> X
    V --> X
    W --> X

