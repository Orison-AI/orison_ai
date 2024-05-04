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
    title = StringField(required=True)
    authors = ListField(StringField())
    citations_received = IntField()
    conference_name = StringField()
    year = IntField()
    impact_factor = FloatField()
    type_of_paper = StringField()
    feedbacks = ListField(StringField())


class GoogleScholarDB(Document):
    name = StringField(required=True)
    position = StringField()
    affiliation = StringField()
    total_citations = IntField()
    publications = ListField(EmbeddedDocumentField(Publication))

    meta = {"collection": "google_scholars"}
