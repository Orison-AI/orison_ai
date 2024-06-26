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


class CREDENTIALS_NOT_FOUND(ValueError):
    def __init__(self, message="Credentials not found"):
        self.message = message
        super().__init__(self.message)


class INVALID_CREDENTIALS(Exception):
    def __init__(self, message="Invalid Credentials"):
        self.message = message
        super().__init__(self.message)


class FIRESTORE_CONNECTION_FAILED(Exception):
    def __init__(self, message="Failed to connect to Firestore"):
        self.message = message
        super().__init__(self.message)


class LLM_INITIALIZATION_FAILED(Exception):
    def __init__(self, message="Failed to initialize LLM model"):
        self.message = message
        super().__init__(self.message)


class QDrant_INITIALIZATION_FAILED(Exception):
    def __init__(self, message="Failed to initialize QDrant client"):
        self.message = message
        super().__init__(self.message)


class Retriever_INITIALIZATION_FAILED(Exception):
    def __init__(self, message="Failed to initialize Retriever"):
        self.message = message
        super().__init__(self.message)
