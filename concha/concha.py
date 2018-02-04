# -*- coding: utf-8 -*-
# Copyright 2018 Pascual de Juan All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
__author__ = 'Pascual de Juan <pascual.dejuan@gmail.com>'
__version__ = '1.0'

import os
import datetime
from connl_tree import text_parse, ConnlTree
from trick import append_trick
from kernel import linker, Artifact
from flask import Flask, request, jsonify, abort

# This is because of the annoying warnings of the standard CPU TF distribution
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # No TF optimization warnings
app = Flask(__name__)
tricks = []
documents = []


@app.route('/v1/tricks', methods=['POST', 'GET'])
@app.route('/v1/tricks/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
def tricks_methods(id_=None):
    """Handles restful methods for tricks resources."""
    response = None
    if id_ is None:
        if request.method == 'POST':
            if not request.json:
                abort(400)
            id_ = len(tricks)
            append_trick(request.json, tricks)
            response = jsonify({"id": id_, "message": "trick {} created Ok".format(id_)})
            response.status_code = 201
        elif request.method == 'GET':
            response = jsonify(tricks)
        else:
            abort(400)
    else:
        if 0 > id_ >= len(tricks):
            abort(404)
        if request.method == 'DELETE':
            tricks.pop(id_)
            response = jsonify({"message": "trick {} deleted Ok".format(id_)})
        elif request.method == 'PUT':
            if not request.json:
                abort(400)
            tricks[id_] = request.json
            response = jsonify({"message": "trick {} modified Ok".format(id_)})
        elif request.method == 'GET':
            response = jsonify(tricks[id_])
        else:
            abort(400)
    return response


@app.route('/v1/documents:analyzeSyntax', methods=['POST'])
def documents_analyze_syntax():
    """Return just a text parsing. No document handling."""
    if not request.json:
        abort(400)
    return jsonify(text_parse(request.json['text']))


@app.route('/v1/documents', methods=['POST', 'GET'])
def documents_methods():
    """Handle restful methods for documents resources."""
    response = None
    if request.method == 'POST':
        if not request.json:
            abort(400)
        id_ = len(documents)  # Append only.
        documents.append({
            'date': str(datetime.datetime.now()).split('.')[0],
            'text': request.json['text']
        })
        doc = text_parse(request.json['text'])
        artifact = linker(doc, tricks)
        response = jsonify({
            'id': id_,
            'answer_text': '{ROOT}'.format_map(artifact.doc),  # TODO error handling
            'request': doc,
            'tricks': artifact.used_tricks
        })
        response.status_code = 201 if artifact.status == '200' else int(artifact.status)
    elif request.method == 'GET':
        response = jsonify(documents)
        response.status_code = 200
    else:
        abort(400)
    return response


if __name__ == '__main__':
    app.run(debug=True)
