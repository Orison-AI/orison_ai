# Orison AI - TODO

## Auth

- Lower priority:
    - Display username in settings
    - Confirmation button and text field before deleting user
    - Google account support
    - Check if account already exists for email before or during user creation
    - Login caching
        - How is user cached? When does it expire?
        - Cache user for a certain amount of time (test a 1 minute expiration, then increase to 1 day or something)
    - Email validation
        - Email confirmation mechanism
        - User creation email notification
        - User deletion email notification
    - Reset password option

## Database

- Upload feature
    - Use icon to indicate drag-n-drop
    - Use button for browsing
    - If file version already uploaded, prompt user to confirm before overwriting
    - Display spinner while uploading that says "Uploading xyz.txt"
    - Clean-up toasts

## Backend Comms

- Deploy a REST API to Google App Engine
- Send messages each way

## Bugs

- Make login inputs double-click selectable
- Deletion
    - Make sure that deleted applicants are also deselected
    - When applicant is deleted, delete all of their documents from filestore
    - When account is deleted, delete all of their applicant's documents from filestore

## Upload Info

- Google scholar link
- LinkedIn
- Personal website
- Multiple buckets of documentsßßßsß
    - Awards
    - Research
    - Reviews
    - Feedback
