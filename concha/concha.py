# -*- coding: utf-8 -*-
import os
import subprocess
import requests
import json
from ConnlTree import ConnlTree
from random import choice
from functools import reduce
from flask import Flask
from flask import request, jsonify, abort

app = Flask(__name__)

# This is because of the annoying warnings of the standard CPU TF distribution
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # No TF optimization warnings
tricks = []
documents = []

REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')


def _parse(text):
    """ Do a external parsing returning it in a CoNNL tree. """
    text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
    shell_cmd = 'echo ' + text + ' | ./parse.sh ../lang_models/Spanish'
    connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
    connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
    result = ConnlTree()
    return result.parse(connl_txt)


def _match_tricks(tricks_, doc):
    """ Identifies which tricks matches with provided CoNNL tree document. """
    candidates = []
    for trick in tricks_:
        if doc.matches(trick['given']):
            candidates.append(trick)
    return candidates


def _expand_trick(trick, doc):
    """ Substitute the 'then' part of a trick according to a document. """
    context = {'d': doc}
    if 'when' in trick:
        if trick['when']['method'] == 'POST':
            uri = trick['when']['uri'].format_map(context)
            response = requests.post(url=uri, json=trick['when']['body'])
            status_code = '{}'.format(response.status_code)
            context.update({'r': {'body': json.loads(response.text)}})
        elif trick['when']['method'] == 'GET':
            uri = trick['when']['uri'].format_map(context)
            response = requests.get(url=uri)
            status_code = '{}'.format(response.status_code)
            context.update({'r': {'body': json.loads(response.text)}})
        else:
            status_code = '400'  # TODO do other methods
    else:
        status_code = '200'
    if status_code in trick['then']:
        then = trick['then'][status_code]
        result = then.format_map(context)
        return result
    else:
        return 'Unknown answer'


@app.route('/v1/tricks', methods=['POST', 'GET'])
@app.route('/v1/tricks/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tricks_methods(id_=None):
    """ Handles restful methods for tricks resources. """
    response = None
    if id_ is None:
        if request.method == 'POST':
            if not request.json:
                abort(400)
            tricks.append(request.json)
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
    """ Handy document handler which just returns a text parsing. """
    if not request.json:
        abort(400)
    return jsonify(_parse(request.json['text']))


@app.route('/v1/documents', methods=['POST', 'GET'])
def documents_methods():
    """ Handles restful methods for documents resources. """
    if request.method == 'POST':
        if not request.json:
            abort(400)
        documents.append({
            # 'date': datetime.now(),
            'text': request.json['text']
        })
        doc = _parse(request.json['text'])
        candidate_tricks = _match_tricks(tricks, doc)
        if len(candidate_tricks) > 0:
            chosen_trick = choice(candidate_tricks)
            expanded_trick = _expand_trick(chosen_trick, doc)
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
