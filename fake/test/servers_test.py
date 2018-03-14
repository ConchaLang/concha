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

import unittest
import fake.servers as servers

SMALL = '{"kind": "small machine"}'
MEDIUM = '{"kind": "medium machine"}'
LARGE = '{"kind": "large machine"}'

PONG = '{"kind": "pong.exe"}'
TETRIS = '{"kind": "tetris.exe"}'
PACMAN = '{"kind": "pacman.exe"}'


def setup_server(app, srv_id, data=None):
    if data:
        return app.post(
            '/v1/servers/{}'.format(srv_id),
            data=data,
            mimetype='application/json')
    else:
        return app.post(
            '/v1/servers/{}'.format(srv_id))


def setup_process(app, srv_id, prc_id, data=None):
    if data:
        return app.post(
            '/v1/servers/{}/processes/{}'.format(srv_id, prc_id),
            data=data,
            mimetype='application/json')
    else:
        return app.post(
            '/v1/servers/{}/processes/{}'.format(srv_id, prc_id))


class ServersTestCase(unittest.TestCase):
    def setUp(self):
        servers.app.testing = True
        self.app = servers.app.test_client()

    def tearDown(self):
        servers.reset()

    def test_empty_servers(self):
        rv = self.app.get('/v1/servers')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'{}' in rv.data)

    def test_empty_filter(self):
        rv = self.app.get('/v1/servers?filter=max_load')

        self.assertTrue(rv.status_code == 404)

    def test_create_server(self):
        rv = setup_server(self.app, 'srv001', SMALL)

        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'started Ok' in rv.data)

    def test_create_server_2ndp_conflict(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = setup_server(self.app, 'srv001', LARGE)

        self.assertTrue(rv.status_code == 409)

    def test_create_server_2ndp_bad_request(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = setup_server(self.app, 'srv002')

        self.assertTrue(rv.status_code == 400)

    def test_read_server(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.get('/v1/servers/srv001')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)

    def test_read_server_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.get('/v1/servers/srv002')

        self.assertTrue(rv.status_code == 404)

    def test_read_servers(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_server(self.app, 'srv007', LARGE)

        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_update_server(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.put('/v1/servers/srv001',
                          data=MEDIUM,
                          mimetype='application/json')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'reconfigured Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'small' in rv.data)
        self.assertTrue(b'medium' in rv.data)

    def test_update_server_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.put('/v1/servers/srv002',
                          data='{"kind": "medium machine"}',
                          mimetype='application/json')

        self.assertTrue(rv.status_code == 404)

    def test_update_server_2ndp_bad_request(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.put('/v1/servers/srv001')

        self.assertTrue(rv.status_code == 400)

    def test_delete_server(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_server(self.app, 'srv007', SMALL)

        rv = self.app.delete('/v1/servers/srv001')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'stopped Ok' in rv.data)
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_delete_server_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_server(self.app, 'srv007', SMALL)

        rv = self.app.delete('/v1/servers/srv002')
        self.assertTrue(rv.status_code == 404)

    def test_empty_processes(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.get('/v1/servers/srv001/processes')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'{}' in rv.data)

    def test_empty_processes_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = self.app.get('/v1/servers/srv002/processes')
        self.assertTrue(rv.status_code == 404)

    def test_create_process(self):
        setup_server(self.app, 'srv001', SMALL)

        rv = setup_process(self.app, 'srv001', 'proc001', TETRIS)

        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'launched Ok' in rv.data)

    def test_create_process_2ndp_conflict(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = setup_process(self.app, 'srv001', 'proc001', PONG)

        self.assertTrue(rv.status_code == 409)

    def test_create_process_2ndp_bad_request(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = setup_process(self.app, 'srv001', 'proc002')

        self.assertTrue(rv.status_code == 400)

    def test_read_process(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.get('/v1/servers/srv001/processes/proc001')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)

    def test_read_process_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.get('/v1/servers/srv001/processes/proc002')
        self.assertTrue(rv.status_code == 404)

    def test_update_process(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.put('/v1/servers/srv001/processes/proc001',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'modified Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pacman' in rv.data)

    def test_update_process_2ndp_process_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.put('/v1/servers/srv001/processes/proc002',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')

        self.assertTrue(rv.status_code == 404)

    def test_update_process_2ndp_server_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.put('/v1/servers/srv002/processes/proc001',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')

        self.assertTrue(rv.status_code == 404)

    def test_update_process_2ndp_bad_request(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.put('/v1/servers/srv001/processes/proc001')

        self.assertTrue(rv.status_code == 400)

    def test_filter_max_load(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)
        setup_server(self.app, 'srv007', LARGE)
        setup_process(self.app, 'srv007', 'proc001', PACMAN)

        rv = self.app.get('/v1/servers?filter=max_load')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)

    def test_filter_max_load_2nd_graceful_unknown_server(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)
        setup_server(self.app, 'srv007', LARGE)
        setup_process(self.app, 'srv007', 'proc001', PACMAN)

        rv = self.app.get('/v1/servers?filter=unknown_filter')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_filter_max_load_2nd_graceful_unknown_filter(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)
        setup_server(self.app, 'srv007', LARGE)
        setup_process(self.app, 'srv007', 'proc001', PACMAN)

        rv = self.app.get('/v1/servers?unknown_query=unknown_filter')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_read_processes(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)

        rv = self.app.get('/v1/servers/srv001/processes')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)

    def test_read_processes_2ndp_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)

        rv = self.app.get('/v1/servers/srv002/processes')

        self.assertTrue(rv.status_code == 404)

    def test_delete_process(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)
        setup_process(self.app, 'srv001', 'proc002', PONG)

        rv = self.app.delete('/v1/servers/srv001/processes/proc001')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'halted Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)

    def test_delete_process_2ndp_process_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.delete('/v1/servers/srv001/processes/proc002')

        self.assertTrue(rv.status_code == 404)

    def test_delete_process_2ndp_server_not_found(self):
        setup_server(self.app, 'srv001', SMALL)
        setup_process(self.app, 'srv001', 'proc001', TETRIS)

        rv = self.app.delete('/v1/servers/srv002/processes/proc001')

        self.assertTrue(rv.status_code == 404)


if __name__ == '__main__':
    unittest.main()
