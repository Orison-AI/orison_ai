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
import logging
import streamlit as st
from orison_ai.src.database.story_client import StoryClient
from orison_ai.src.database.models import StoryBuilderDB

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

client = StoryClient()


class StoryBuilderApp:
    def __init__(self, attorney_id, user_id, side_bar):
        self._attorney_id = attorney_id
        self._user_id = user_id
        self._sidebar = side_bar

    def _display_qa_pairs(self, qa_pairs):
        # Custom HTML and CSS to style the markdown for questions and answers
        st.markdown(
            """
        <style>
        .question {
            font-family: Arial;
            font-size: 18px;
            color: #3c3c3c;
            background-color: #b4b4b4;
            padding: 10px;
            border-radius: 5px;
        }
        .answer {
            font-family: Arial;
            font-size: 16px;
            color: #3c3c3c;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-top: 5px;
        }
        .source {
            font-family: Arial;
            font-size: 16px;
            color: #3c3c3c;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-top: 5px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Loop through each question-answer pair
        for i in range(0, len(qa_pairs) - 1, 3):
            st.markdown(
                f'<div class="question">{qa_pairs[i]}</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="answer">{qa_pairs[i+1]}</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="source">{qa_pairs[i+2]}</div>', unsafe_allow_html=True
            )

    async def run(self):
        """
        Fetches the story data from the database and displays it on the Streamlit app
        """
        if self._sidebar == "StoryBuilder":
            # story = StoryBuilderDB()
            story = await client.find_top(
                attorney_id=self._attorney_id,
                user_id=self._user_id,
                filters={"type_of_story": "detailed"},
            )
            _logger.info(f"Obtained story data:\n {story.to_json()}")
            response = []
            for qanda in story.summary:
                response.append(qanda.question)
                response.append(qanda.answer)
                response.append(qanda.source)

            st.title(self._sidebar)
            self._display_qa_pairs(response)

        elif self._sidebar == "Screening":
            # story = StoryBuilderDB()
            story = await client.find_top(
                attorney_id=self._attorney_id,
                user_id=self._user_id,
                filters={"type_of_story": "preliminary"},
            )
            _logger.info(f"Obtained story data:\n {story.to_json()}")
            response = []
            for qanda in story.summary:
                response.append(qanda.question)
                response.append(qanda.answer)
                response.append(qanda.source)
            st.title(self._sidebar)
            self._display_qa_pairs(response)


if __name__ == "__main__":

    async def helper():
        story_app = StoryBuilderApp(
            attorney_id="demo_v2", user_id="rmalhan", side_bar="Screening"
        )
        await story_app.run()
        story_app = StoryBuilderApp(
            attorney_id="demo_v2", user_id="rmalhan", side_bar="StoryBuilder"
        )
        await story_app.run()

    asyncio.run(helper())
