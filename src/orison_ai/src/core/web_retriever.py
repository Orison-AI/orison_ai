#! /usr/bin/env python3.9

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

from orison_ai.src.database.google_scholar_collection import GoogleScholarClient
from orison_ai.src.web_extractors.extractors import (
    get_google_scholar_info,
)
import traceback
import asyncio
from orison_ai.src.utils.constants import DB_NAME


if __name__ == "__main__":
    user_id = "rmalhan"
    client = GoogleScholarClient(user_id=user_id, db_name=DB_NAME)
    scholar_link = "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"

    if scholar_link != "":
        try:
            scholar_info = get_google_scholar_info(scholar_link)
        except Exception as e:
            print(
                f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
            )

        if scholar_info is not None:
            scholar_info.user_id = user_id
            asyncio.run(client.insert(scholar_info))
