#! /usr/bin/env python3.10

import asyncio

# TODO: Do some import magic here to shorten the import path
from orison_ai.src.cloud.storage.firebase_storage import FirebaseStorage


async def helper():
    remote_path: str = (
        "documents/attorneys/mygD1yNiFNNan9N4QuxPPZ0pAYJ3/applicants/onhVrRMv7rOKqfkvjJxu/test.md"
    )
    local_path: str = "/app/vault/junk/downloaded_file"
    await FirebaseStorage.download_file(
        remote_path=remote_path, local_file_path=local_path
    )


asyncio.run(helper())
