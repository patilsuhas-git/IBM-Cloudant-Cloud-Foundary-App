# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify,  make_response
from cloudant.client import Cloudant

credential = {
}

def create_document() :
    client = Cloudant(credential['username'], credential['password'], url=credential['url'])
    client.connect()
    db = client['cc_6331']
    data = {
    '_id': 'julia31', # Setting _id is optional
    'name': 'Julia',
    'age': 30,
    'pets': ['cat', 'dog', 'frog']
    }

    # Create a document using the Database API
    db.create_document(data)
    client.disconnect()

create_document()
