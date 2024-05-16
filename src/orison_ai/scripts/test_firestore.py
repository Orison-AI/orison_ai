#! /usr/bin/env python3.10

import asyncio
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from orison_ai.src.database.models import GoogleScholarDB
from orison_ai.src.core.google_scholar import get_google_scholar_info
from orison_ai.src.database.google_scholar_client import GoogleScholarClient

# cred = credentials.Certificate("/app/vault/credentials/firebase.json")

# app = firebase_admin.initialize_app(cred)
# client = firestore.client(app)
# collection = client.collection(GoogleScholarDB.__name__)

scholar_client = GoogleScholarClient()

# applicant_id = "rmalhan"
# user_id = "demo_v2"
# scholar_link = "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"
# scholar_info = asyncio.run(get_google_scholar_info(user_id, applicant_id, scholar_link))
# asyncio.run(scholar_client.insert(scholar_info))


async def helper():
    await scholar_client.find_top("demo_v2", "rmalhan")
    await scholar_client.find_top("demo_v2", "rmalhan")


result = asyncio.run(helper())
# import IPython

# IPython.embed()
