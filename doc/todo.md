# Orison AI - TODO

## Auth

- Higher priority:
    - Header
        - Background
        - Logout button in header
    - Smoke tests
        - Verify user sign-in works
    - Settings
        - ColorModeToggle
        - Display username in settings
        - Option to delete user in settings, with confirmation pop-up -- need to log them out and delete the user

- Lower priority:
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

- Upload docs
- Store docs in the cloud
- Delete docs

## Backend Comms

- Deploy a REST API to Google App Engine
- Send messages each way