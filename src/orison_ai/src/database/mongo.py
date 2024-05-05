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

import pymongo
from pymongo import MongoClient


class MongoDB:
    def __init__(self, db_name, collection_name, db_path="mongodb://mongodb:27017/"):
        self.client = MongoClient(db_path, serverSelectionTimeoutMS=1000)
        self.db = self.client[db_name]
        self.collection_name = collection_name
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        result = self.collection.insert_one(data)
        print(f"Inserted data \n{data}\n with ID: {result.inserted_id}")

    def retrieve_data(self):
        latest_data = self.collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        return latest_data
