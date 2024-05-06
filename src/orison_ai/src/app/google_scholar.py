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

import streamlit as st
import asyncio
import logging
from orison_ai.src.web_extractors.utils import generate_scholar_message
import traceback
from orison_ai.src.utils.constants import DB_NAME
from orison_ai.src.database.google_scholar_collection import GoogleScholarClient

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class GoogleScholarApp:
    def __init__(self, user_id, side_bar):
        self._user_id = user_id
        self._sidebar = side_bar
        self._mongo_client = GoogleScholarClient(user_id=self._user_id, db_name=DB_NAME)
        self.run()

    def run(self):
        if not self._sidebar == "Informatics":
            return

        try:
            _logger.info("Fetching google scholar data.")
            scholar_info = asyncio.run(self._mongo_client.find_one(self._user_id))
            _logger.info(f"Obtained google scholar data:\n {scholar_info}")
            if scholar_info is not None:
                st.write(generate_scholar_message(scholar_info))
            else:
                _logger.warning("Google scholar data is None.")
        except Exception as e:
            _logger.error(
                f"Failed to obtain google scholar data. Error: {traceback.format_exc(e)}"
            )
