# -*- coding: utf-8 -*-
import os
import subprocess
from trick import append_trick, expand_trick, match_tricks
from connl_tree import ConnlTree
from random import choice
from functools import reduce
from flask import Flask
from flask import request, jsonify, abort

app = Flask(__name__)

# This is because of the annoying warnings of the standard CPU TF distribution
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # No TF optimization warnings
documents = []

REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')

tricks = []


def _parse(text):
    """Do a external parsing returning it in a CoNNL tree."""
    text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
    shell_cmd = 'echo ' + text + ' | ./parse.sh ../lang_models/Spanish'
    connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
    connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
    result = ConnlTree()
    return result.parse(connl_txt)


@app.route('/v1/tricks', methods=['POST', 'GET'])
@app.route('/v1/tricks/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tricks_methods(id_=None):
    """Handles restful methods for tricks resources."""
    response = None
    if id_ is None:
        if request.method == 'POST':
            if not request.json:
                abort(400)
            append_trick(request.json, tricks)
            response = jsonify({"message": "trick {} created Ok".format(len(tricks)-1)})
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
    """Return just a text parsing."""
    if not request.json:
        abort(400)
    return jsonify(_parse(request.json['text']))


@app.route('/v1/documents', methods=['POST', 'GET'])
def documents_methods():
    """Handle restful methods for documents resources."""
    if request.method == 'POST':
        if not request.json:
            abort(400)
        documents.append({
            # 'date': datetime.now(),
            'text': request.json['text']
        })
        doc = _parse(request.json['text'])
        candidate_tricks = match_tricks(doc, tricks)
        if len(candidate_tricks) > 0:
            chosen_trick = choice(candidate_tricks)
            expanded_trick = expand_trick(chosen_trick, doc)
            response = jsonify({'answer_text': expanded_trick, 'request': doc, 'trick': chosen_trick})
            response.status_code = 201
        else:
            response = jsonify({'answer_text': 'No trick', 'request': doc})  # TODO not in English
            response.status_code = 404
    else:  # 'GET'
        response = jsonify(documents)
        response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(debug=True)
