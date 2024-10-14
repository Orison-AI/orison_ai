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


class OrisonMessenger_INITIALIZATION_FAILED(Exception):
    def __init__(
        self, message="Failed to initialize OrisonMessenger", exception="UNKNOWN"
    ):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class CREDENTIALS_NOT_FOUND(ValueError):
    def __init__(self, message="Credentials not found", exception="UNKNOWN"):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class INVALID_CREDENTIALS(Exception):
    def __init__(self, message="Invalid Credentials", exception="UNKNOWN"):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class FIRESTORE_CONNECTION_FAILED(Exception):
    def __init__(self, message="Failed to connect to Firestore", exception="UNKNOWN"):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class LLM_INITIALIZATION_FAILED(Exception):
    def __init__(self, message="Failed to initialize LLM model", exception="UNKNOWN"):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class QDrant_INITIALIZATION_FAILED(Exception):
    def __init__(
        self, message="Failed to initialize QDrant client", exception="UNKNOWN"
    ):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class Retriever_INITIALIZATION_FAILED(Exception):
    def __init__(self, message="Failed to initialize Retriever", exception="UNKNOWN"):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)


class RateLimiter_INITIALIZATION_FAILED(Exception):
    def __init__(
        self, message="Failed to initialize Rate Limiter", exception="UNKNOWN"
    ):
        self.message = message + " . Error: " + str(exception)
        super().__init__(self.message)
