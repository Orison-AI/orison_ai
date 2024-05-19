
# Orison AI - Notes

## Immigration Application Process

- Initial applicant evaluation
    - $500-$1000 cost to applicant (some attorneys may do it for free)

## IP

- StoryBuilder/storybuilder
    - Used by attorneys to upload applicant documentation and view data about the applicant.
- Where do I stand?
    - Used by visa applicants to check how they stack up against other applicants.

## Firebase Admin VS FireStore
- Firebase admin is to be used with backend SDK whereas firestore is suitable for web client
- Firebase admin uses service account key that needs to be created after changing organization permissions

## The current UI is being built too specific to EB-1 A, B, or O1 cases
- Additional UI changes would be needed for L1 cases

## Deploying gcloud function
- gcloud functions deploy fetch_scholar --runtime python310 --trigger-http --allow-unauthenticated --no-gen2

## Testing gcloud
- functions-framework --target=func_name --debug