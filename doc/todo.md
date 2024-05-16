# Orison AI - TODO

## Applicant Files

- Change page name to "Applicant Files"
- Use icon to indicate drag-n-drop
- Use button for browsing
- If file version already uploaded, prompt user to confirm before overwriting
- Display spinner while uploading that says "Uploading xyz.txt"
- Clean-up toasts
- Split doc uploading into 4 buckets:
    - Awards
    - Research
    - Reviews
    - Feedback

## Google Scholar

- Create page for Google Scholar fetching and review (fetch command not yet implemented)

## Backend Comms

- Deploy a REST API to Google App Engine
- Implement Google Scholar fetching command

## LinkedIn

- Create page for LinkedIn fetching and review

## Personal Website

- Create page for personal website fetching and review

## Bugs

- Make applicant fields editable via single click
- Deletion
    - When applicant is deleted, delete all of their documents from filestore
    - When account is deleted, delete all of their applicant's documents from filestore

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
