#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

import os
import pyrebase

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyD-DL2nGP24pCQE9ySboRrRp638MvSKV0M",
    "authDomain": "orison-ai-visa-apply.firebaseapp.com",
    "projectId": "orison-ai-visa-apply",
    "storageBucket": "orison-ai-visa-apply.appspot.com",
    "messagingSenderId": "685108028813",
    "appId": "1:685108028813:web:06164ab1ea0a4f765089c4",
    "measurementId": "G-0X5RE57SDJ",
    "databaseURL": "",
}


def get_firebase_identity_token():
    # Initialize Firebase
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()

    # Authenticate user
    email = "admin@orison.ai"
    password = os.getenv("ORISON_PASSWORD")
    user = auth.sign_in_with_email_and_password(email, password)

    # Get ID token
    id_token = user["idToken"]

    return id_token


if __name__ == "__main__":
    id_token = get_firebase_identity_token()
    print(id_token)
