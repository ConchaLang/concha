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
import subprocess
import datetime
from trick import append_trick
from connl_tree import ConnlTree
from linker import link
from functools import reduce
from flask import Flask
from flask import request, jsonify, abort

app = Flask(__name__)
tricks = []
documents = []
REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')

# This is because of the annoying warnings of the standard CPU TF distribution
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # No TF optimization warnings


def parse(text):
    """Do a external parsing returning it in a CoNNL tree. It can evolve to other invocation ways"""
    text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
    shell_cmd = 'echo ' + text + ' | ./parse.sh ../lang_models/Spanish'
    connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
    connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
    result = ConnlTree()
    return result.parse(connl_txt)


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
    return jsonify(_parse(request.json['text']))


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
        doc = parse(request.json['text'])
        treated_doc = link(doc, tricks)
        response = jsonify({"id": id_, 'answer_text': treated_doc.treat, 'request': doc, 'tricks': treated_doc.tricks})
        response.status_code = treated_doc.status
    elif request.method == 'GET':
        response = jsonify(documents)
        response.status_code = 200
    else:
        abort(400)
    return response


if __name__ == '__main__':
    app.run(debug=True)
