#! /usr/bin/env python3.8

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


def generate_scholar_message(scholar_info):
    message = ""
    message = "\n".join(
        [message, _message_append_helper("Candidate Name", scholar_info.name)]
    )
    message = "\n".join(
        [message, _message_append_helper("Candidate Position", scholar_info.position)]
    )
    message = "\n".join(
        [
            message,
            _message_append_helper("Citation Count", scholar_info.total_citations),
        ]
    )
    message = "\n\n".join([message, "Publications:"])
    message = "\n".join([message, _publication_helper(scholar_info.publications)])
    return message


def _message_append_helper(text, field):
    if field is None:
        return ""
    if isinstance(field, str):
        if field == "":
            return ""
    return f"{text}: {field}"


def _publication_helper(publications):
    message = ""
    for publication in publications:
        message = "\n\n".join(
            [message, _message_append_helper("Title", publication.title)]
        )
        message = "\n".join(
            [message, _message_append_helper("Authors", publication.authors)]
        )
        message = "\n".join(
            [
                message,
                _message_append_helper(
                    "Citations Received", publication.citations_received
                ),
            ]
        )
        message = "\n".join(
            [
                message,
                _message_append_helper("Conference Name", publication.conference_name),
            ]
        )
        message = "\n".join([message, _message_append_helper("Year", publication.year)])
        message = "\n".join(
            [
                message,
                _message_append_helper("Impact Factor", publication.impact_factor),
            ]
        )
        message = "\n".join(
            [
                message,
                _message_append_helper("Type of Paper", publication.type_of_paper),
            ]
        )
        message = "\n".join(
            [message, _message_append_helper("Feedbacks", publication.feedbacks)]
        )
    return message
