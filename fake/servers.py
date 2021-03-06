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
import argparse

app = Flask(__name__)
_servers = {}


def reset():
    global _servers
    _servers = {}


@app.route('/v1/servers', methods=['GET'])
@app.route('/v1/servers/<server_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def servers_methods(server_id=None):
    response = None
    if server_id is None:
        if request.method == 'GET':
            if request.args:
                filter_value = request.args.get('filter')
                if filter_value == 'max_load':
                    max_load_server = max(_servers.values(), key=(lambda v: v['load'])) if _servers else None
                    if max_load_server:
                        response = jsonify(max_load_server)
                    else:
                        abort(404)
                else:  # Unknown filter or query param = gracefully no filter
                    response = jsonify(_servers)
            else:
                response = jsonify(_servers)
        else:
            abort(400)
    else:
        if request.method == 'POST':
            if server_id in _servers:
                abort(409)
            if not request.json:
                abort(400)
            _servers[server_id] = {'name': server_id, 'description': request.json, 'processes': {}, 'load': 0}
            response = jsonify({"message": "server {} started Ok".format(server_id)})
            response.status_code = 201
        else:
            if server_id not in _servers:
                abort(404)
            if request.method == 'DELETE':
                del _servers[server_id]
                response = jsonify({"message": "server {} stopped Ok".format(server_id)})
            elif request.method == 'PUT':
                if not request.json:
                    abort(400)
                _servers[server_id]['description'] = request.json
                response = jsonify({"message": "server {} reconfigured Ok".format(server_id)})
            elif request.method == 'GET':
                response = jsonify(_servers[server_id])
            else:
                abort(400)
    return response


@app.route('/v1/servers/<server_id>/processes', methods=['GET'])
@app.route('/v1/servers/<server_id>/processes/<process_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def processes_methods(server_id, process_id=None):
    if server_id not in _servers:
        abort(404)
    server = _servers[server_id]
    response = None
    if process_id is None:
        if request.method == 'GET':
            response = jsonify(server['processes'])
        else:
            abort(400)
    else:
        if request.method == 'POST':
            if process_id in server['processes']:
                abort(409)
            if not request.json:
                abort(400)
            server['processes'][process_id] = {'name': process_id, 'description': request.json}
            server['load'] += 10
            response = jsonify({"message": "process {} launched Ok in server {}".format(process_id, server_id)})
            response.status_code = 201
        else:
            if process_id not in server['processes']:
                abort(404)
            if request.method == 'DELETE':
                del server['processes'][process_id]
                response = jsonify({"message": "process {} halted Ok in server {}".format(process_id, server_id)})
                server['load'] -= 10
            elif request.method == 'PUT':
                if not request.json:
                    abort(400)
                server['processes'][process_id]['description'] = request.json
                response = jsonify({"message": "process {} modified Ok in server {}".format(process_id, server_id)})
            elif request.method == 'GET':
                response = jsonify(server['processes'][process_id])
            else:
                abort(400)
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Exposes a HTTP fake cloud management mock service.')
    parser.add_argument('-i', '--ip', type=str, default='0.0.0.0',
                        help='listen to the IP address')
    parser.add_argument('-p', '--port', type=int, default=6000,
                        help='listen to the port number')
    parser.add_argument('-X', '--debug', action="store_true",
                        help='debug mode')
    args = parser.parse_args()
    app.run(host=args.ip, port=args.port, debug=args.debug)
