# -*- coding: utf-8 -*-
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
