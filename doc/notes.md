
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

## Deploying and testing gcloud function
- gcloud functions deploy fetch_scholar --runtime python310 --trigger-http --allow-unauthenticated --no-gen2
- curl -m 70 -X POST https://us-central1-orison-ai-visa-apply.cloudfunctions.net/fetch_scholar -H "Authorization: bearer $(gcloud auth print-identity-token)" -H "Content-Type: application/json" -d '{<json message>}'
- Secret manager is the tool used to store access keys like Firebase credentials and github ssh keys
- Having common source code as a separate package is scalable and maintainable. However, gcloud deploy
becomes tricky because now pip needs github path to install the package
- Using private access token is a bad idea and ssh is a safer route
- However ssh is better and procedure is outlined in:
https://cloud.google.com/build/docs/access-github-from-build
- ssh keys are added and cloudbuild.yaml created
- Use the command: gcloud builds submit --config=cloudbuild.yaml
- Gave up on ssh

## Cloud Secret Manager
- Uploaded firebase_credentials.json to secret manager and gave permissions to project
- Ran this on command line to grant access to gcloud
gcloud secrets add-iam-policy-binding firebase_credentials \
    --role roles/secretmanager.secretAccessor \
    --member serviceAccount:orison-ai-visa-apply@appspot.gserviceaccount.com
- The credentials can be accessed using google cloud secret manager

## Testing gcloud
- functions-framework --target=func_name --debug

## ToDo:
- SSH access by a google function to pip install its dependencies from orison github