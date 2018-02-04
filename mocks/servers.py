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

from flask import Flask
from flask import request, jsonify, abort

app = Flask(__name__)


servers = {}


@app.route('/v1/servers', methods=['GET'])
@app.route('/v1/servers/<id_>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def servers_methods(id_=None):
    response = None
    if id_ is None:
        if request.method == 'GET':
            response = jsonify(servers)
        else:
            abort(400)
    else:
        if request.method == 'POST':
            if id_ in servers:
                abort(409)
            if not request.json:
                abort(400)
            servers[id_] = {'description': request.json, 'load': 0.1234}
            response = jsonify({"message": "server {} created Ok".format(id_)})
            response.status_code = 201
        else:
            if id_ not in servers:
                abort(404)
            if request.method == 'DELETE':
                del servers[id_]
                response = jsonify({"message": "server {} deleted Ok".format(id_)})
            elif request.method == 'PUT':
                if not request.json:
                    abort(400)
                servers[id_] = {'description': request.json, 'load': 0.5678}
                response = jsonify({"message": "server {} modified Ok".format(id_)})
            elif request.method == 'GET':
                response = jsonify(servers[id_])
            else:
                abort(400)
    return response


@app.route('/v1/servers/<_id>/load', methods=['GET'])
def servers_id_load(id_=None):
    response = None
    if id is not None:
        if id_ not in servers:
            abort(404)
        response = jsonify(servers[id_]['load'])
    else:
        abort(400)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=6000)
