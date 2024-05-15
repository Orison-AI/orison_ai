#! /usr/bin/env python3.10

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

import asyncio
import streamlit as st
from orison_ai.src.api.informatics import GoogleScholarApp
from orison_ai.src.api.story_builder import StoryBuilderApp

# Set page background color
st.markdown(
    """
    <style>
    body {
        background-color: #787878;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set sidebar width
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        width: 250px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Streamlit app
class OrisonApp:
    def __init__(self):
        self._logged_in = None
        self._user_id = ""
        self._attorney_id = "demo_v2"
        self._google_scholar = None
        self._story_builder = None
        self._informatics = None
        self._pages = False
        self._sidebar = None
        asyncio.run(self._initialize())

    async def _initialize_pages(self):
        pages = [
            "Dashboard",
            "Upload",
            "Screening",
            "StoryBuilder",
            "DocBot",
            "Informatics",
            "CompareAI",
        ]
        # Create sidebar with tabs
        self._sidebar = st.sidebar.radio("Navigation", pages)

        if not self._google_scholar:
            self._google_scholar = GoogleScholarApp(
                self._attorney_id, self._user_id, self._sidebar
            )
        if not self._story_builder:
            self._story_builder = StoryBuilderApp(
                self._attorney_id, self._user_id, self._sidebar
            )

        await self._google_scholar.run()
        await self._story_builder.run()
        self._pages = True

    async def _initialize(self):
        st.title("Orison AI")

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
            self._logged_in = False

        if st.session_state.logged_in:
            self._user_id = st.session_state.user_id
            self._logged_in = True
            if not self._pages:
                await self._initialize_pages()

            if st.button("Log out"):
                st.session_state.logged_in = False
                self._logged_in = False
                st.rerun()
        else:
            # User login interface
            user_id = st.text_input("Enter your user ID to log in", "")

            if st.button("Log in") and user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.rerun()


if __name__ == "__main__":
    app = OrisonApp()
