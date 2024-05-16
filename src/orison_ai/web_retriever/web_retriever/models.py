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

# External

from dataclasses import dataclass
from datetime import datetime
from mongoengine import (
    Document,
    IntField,
    StringField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    DateTimeField,
    DictField,
)


@dataclass
class GoogleScholarRequest:
    attorney_id: str
    applicant_id: str
    scholar_link: str


@dataclass
class GoogleScholarResponse:
    message: str
    status: int


class BaseModel(Document):
    name = StringField()
    email = StringField()
    attorney_id = StringField(required=True)
    applicant_id = StringField(required=True)
    date_created = DateTimeField(required=True, default=datetime.utcnow())
    phone = StringField()
    address = StringField()
    city = StringField()
    state = StringField()
    country = StringField()
    zip_code = StringField()
    googlescholar = StringField()
    linkedin = StringField()
    github = StringField()
    twitter = StringField()
    facebook = StringField()
    instagram = StringField()
    website = StringField()
    meta = {"allow_inheritance": True}


class Author(EmbeddedDocument):
    profile_link = StringField(required=True)
    scholar_id = StringField()
    name = StringField(required=True)
    designation = StringField()
    affiliation = StringField()


class Publication(EmbeddedDocument):
    """
    MongoDB document class for a Publication detail of the applicant
    """

    title = StringField(required=True)
    authors = ListField(StringField())
    cited_by = IntField()
    forum_name = StringField()
    publisher = StringField()
    abstract = StringField()
    year = IntField()
    impact_factor = FloatField()
    type_of_paper = StringField()  # Conference Journal Article etc
    peer_reviews = ListField(StringField())


class GoogleScholarDB(BaseModel):
    """
    MongoDB document class for Google scholar details of the applicant
    """

    author = EmbeddedDocumentField(Author)
    co_authors = ListField(EmbeddedDocumentField(Author))
    keywords = ListField(StringField())
    cited_by = IntField()
    h_index = IntField()
    cited_by_5y = IntField()
    h_index_5y = IntField()
    cited_each_year = DictField()
    publications = ListField(EmbeddedDocumentField(Publication))
    homepage = StringField()
    other_details = DictField()
