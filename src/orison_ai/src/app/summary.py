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
import os
import sys


class Summary:
    def __init__(self, side_bar, mongo_client):
        self._mongo_client = mongo_client
        self._sidebar = side_bar
        self._info = ""
        self.run()

    def publish_info(self, page, information):
        self._info = "\n\n".join([self._info, information])

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
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Loop through each question-answer pair
        for i in range(0, len(qa_pairs) - 1, 2):
            st.markdown(
                f'<div class="question">{qa_pairs[i]}</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="answer">{qa_pairs[i+1]}</div>', unsafe_allow_html=True
            )

    def run(self):
        """ """
        if self._sidebar == "Summary":
            latest_data = self._mongo_client.retrieve_data()["Summary"]
            response = []
            for question in latest_data.keys():
                response.append(question)
                response.append(latest_data[question])

            st.title(self._sidebar)
            self._display_qa_pairs(response)
