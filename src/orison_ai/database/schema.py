#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
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

from dataclasses import dataclass
from datetime import datetime, timezone
from mongoengine import (
    Document,
    IntField,
    StringField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    DateTimeField,
    DictField,
)


class BaseModel(Document):
    """Base model for all database documents - preserved from original"""

    name = StringField()
    email = StringField()
    attorney_id = StringField(required=True)
    applicant_id = StringField(required=True)
    date_created = DateTimeField(required=True, default=datetime.now(timezone.utc))
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


@dataclass
class GoogleScholarRequest:
    """Request structure for Google Scholar operations"""

    attorney_id: str
    applicant_id: str
    scholar_link: str


@dataclass
class GoogleScholarResponse:
    """Response structure for Google Scholar operations"""

    message: str
    status: int


class Author(EmbeddedDocument):
    """Author information for publications - preserved from original"""

    profile_link = StringField(required=True)
    name = StringField()
    scholar_id = StringField()
    affiliation = StringField()
    email = StringField()
    interests = ListField(StringField())
    cited_by = IntField()
    h_index = IntField()
    i10_index = IntField()

    def to_json(self):
        """Convert to JSON"""
        return {
            "profile_link": self.profile_link,
            "name": self.name,
            "scholar_id": self.scholar_id,
            "affiliation": self.affiliation,
            "email": self.email,
            "interests": self.interests,
            "cited_by": self.cited_by,
            "h_index": self.h_index,
            "i10_index": self.i10_index,
        }


class Publication(EmbeddedDocument):
    """Publication information - preserved from original"""

    title = StringField(required=True)
    year = StringField()
    authors = StringField()
    abstract = StringField()
    cited_by = IntField()
    forum_name = StringField()
    type_of_paper = StringField()
    peer_reviews = StringField()

    def to_json(self):
        """Convert to JSON"""
        return {
            "title": self.title,
            "year": self.year,
            "authors": self.authors,
            "abstract": self.abstract,
            "cited_by": self.cited_by,
            "forum_name": self.forum_name,
            "type_of_paper": self.type_of_paper,
            "peer_reviews": self.peer_reviews,
        }


class ScholarSummary(EmbeddedDocument):
    """Scholar summary with enhanced information"""

    name = StringField()
    scholar_id = StringField()
    citations = IntField()
    h_index = IntField()
    publication_count = IntField()
    affiliation = StringField()
    email = StringField()
    interests = ListField(StringField())
    i10_index = IntField()
    profile_link = StringField()

    def to_json(self):
        """Convert to JSON"""
        return {
            "name": self.name,
            "scholar_id": self.scholar_id,
            "citations": self.citations,
            "h_index": self.h_index,
            "publication_count": self.publication_count,
            "affiliation": self.affiliation,
            "email": self.email,
            "interests": self.interests,
            "i10_index": self.i10_index,
            "profile_link": self.profile_link,
        }


class QandA(EmbeddedDocument):
    """Question and Answer structure - preserved exactly from original"""

    question = StringField(required=True)
    answer = StringField(required=True)
    source = StringField()


class MemoryEntry(EmbeddedDocument):
    """Memory entry for chat history - preserved from original"""

    user_message = StringField(required=True)
    assistant_response = StringField(required=True)
    timestamp = DateTimeField(default=datetime.now(timezone.utc))


# Main document models
class GoogleScholarDB(BaseModel):
    """Google Scholar database model - preserved from original"""

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

    def to_json(self):
        """Convert to JSON - preserved from original"""
        return {
            "author": self.author.to_json() if self.author else None,
            "co_authors": (
                [coauthor.to_json() for coauthor in self.co_authors]
                if self.co_authors
                else []
            ),
            "keywords": self.keywords,
            "cited_by": self.cited_by,
            "h_index": self.h_index,
            "cited_by_5y": self.cited_by_5y,
            "h_index_5y": self.h_index_5y,
            "cited_each_year": self.cited_each_year,
            "publications": (
                [pub.to_json() for pub in self.publications]
                if self.publications
                else []
            ),
            "homepage": self.homepage,
            "other_details": self.other_details,
        }


class GoogleScholarNetworkDB(BaseModel):
    """Google Scholar network model with enhanced metadata"""

    network = ListField(EmbeddedDocumentField(ScholarSummary), default=[])
    root_scholar_id = StringField()
    root_scholar_name = StringField()
    network_size = IntField()
    max_depth = IntField()
    date_built = DateTimeField(default=datetime.now(timezone.utc))

    def to_json(self):
        """Convert to JSON"""
        return {
            "network": [scholar.to_json() for scholar in self.network],
            "root_scholar_id": self.root_scholar_id,
            "root_scholar_name": self.root_scholar_name,
            "network_size": self.network_size,
            "max_depth": self.max_depth,
            "date_built": self.date_built.isoformat() if self.date_built else None,
        }


class StoryBuilder(BaseModel):
    """Story builder model - preserved from original"""

    summary = ListField(EmbeddedDocumentField(QandA), default=[])


class ScreeningBuilder(BaseModel):
    """Screening builder model - preserved from original"""

    summary = ListField(EmbeddedDocumentField(QandA), default=[])


class EvidenceBuilder(BaseModel):
    """Evidence builder model - preserved from original"""

    summary = StringField()


class ChatMemoryDB(Document):
    """Chat memory database model - preserved from original"""

    attorney_id = StringField(required=True)
    applicant_id = StringField(required=True)
    date_created = DateTimeField(required=True, default=datetime.now(timezone.utc))
    history = ListField(EmbeddedDocumentField(MemoryEntry), default=[])
    date_updated = DateTimeField(default=datetime.now(timezone.utc))

    meta = {
        "collection": "chat_memory",
        "indexes": [
            {"fields": ["applicant_id", "attorney_id"], "unique": True},
        ],
    }
