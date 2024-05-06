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

from mongoengine import (
    Document,
    IntField,
    StringField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
)


class Publication(EmbeddedDocument):
    """
    MongoDB document class for a Publication detail of the applicant
    """

    title = StringField(required=True)
    authors = ListField(StringField())
    citations_received = IntField()
    conference_name = StringField()
    year = IntField()
    impact_factor = FloatField()
    type_of_paper = StringField()
    peer_reviews = ListField(StringField())


class GoogleScholarDB(Document):
    """
    MongoDB document class for Google scholar details of the applicant
    """

    _id = StringField()
    user_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    designation = StringField()
    affiliation = StringField()
    total_citations = IntField()
    publications = ListField(EmbeddedDocumentField(Publication))
    other_details = StringField()


class QandA(EmbeddedDocument):
    """
    MongoDB document class for QandA details of the applicant
    """

    question = StringField(required=True)
    answer = StringField(required=True)


class Story(Document):
    """
    MongoDB document class for Story of the applicant
    """

    user_id = StringField(required=True, unique=True)
    summary = ListField(EmbeddedDocumentField(QandA))
