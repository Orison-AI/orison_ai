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


class Upload:
    def __init__(self, applicant_id, side_bar):
        self._applicant_id = applicant_id
        self._sidebar = side_bar
        self._scholar_link = st.sidebar.text_input(
            label="#### Your Google Scholar Link 👇",
            placeholder="Your Google Scholar Link",
            type="default",
        )

    def run(self):
        pass
