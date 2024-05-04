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

import os
import sys

import streamlit as st
from collections import defaultdict
from orison_ai.src.web_extractors.extractors import (
    get_google_scholar_info,
    get_portfolio_info,
)
from orison_ai.src.database.models import GoogleScholarDB, Publication
from orison_ai.src.database.utils import generate_scholar_message
import traceback


class FeedPoint:
    def __init__(self, side_bar, mongo_client):
        self._mongo_client = mongo_client
        self._sidebar = side_bar
        self._scholar_link = st.sidebar.text_input(
            label="#### Your Google Scholar Link 👇",
            placeholder="Your Google Scholar Link",
            type="default",
        )

        self._portfolio = st.sidebar.text_input(
            label="#### Your Portfolio Link 👇",
            placeholder="Your Portfolio Link",
            type="default",
        )
        self.run()

    def run(self):
        """
        My google scholar link:
        https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao

        Portfolio
        https://www.rmalhan.com/
        """
        st.title(self._sidebar)

        self._scholar_link = (
            "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao"
        )

        if not self._sidebar == "Informatics":
            return

        if self._scholar_link != "":
            try:
                scholar_info = get_google_scholar_info(self._scholar_link)
                if scholar_info is not None:
                    st.write(generate_scholar_message(scholar_info))
            except Exception as e:
                print(
                    f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
                )

        if self._portfolio != "":
            try:
                info = get_portfolio_info(self._portfolio)
                if info is not None or info != "":
                    self.publish_info("Informatics", info)
                self._portfolio = ""
            except:
                self._portfolio = ""
                pass
