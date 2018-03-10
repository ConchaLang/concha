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

import mocks.servers as servers
import unittest


class ServersTestCase(unittest.TestCase):
    def setUp(self):
        servers.app.config['TESTING'] = True
        self.app = servers.app.test_client()

    def test_01_empty_servers(self):
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'{}' in rv.data)

    def test_02_empty_filter(self):
        rv = self.app.get('/v1/servers?filter=max_load')
        self.assertTrue(rv.status_code == 404)

    def test_03_create_server(self):
        rv = self.app.post('/v1/servers/srv001',
                           data='{"kind": "small machine"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'started Ok' in rv.data)
        # Secondary path (conflict)
        rv = self.app.post('/v1/servers/srv001',
                           data='{"kind": "large machine"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 409)
        # Secondary path (bad request)
        rv = self.app.post('/v1/servers/srv002')
        self.assertTrue(rv.status_code == 400)

    def test_04_read_server(self):
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        # Secondary path (not found)
        rv = self.app.get('/v1/servers/srv002')
        self.assertTrue(rv.status_code == 404)

    def test_05_update_server(self):
        rv = self.app.put('/v1/servers/srv001',
                          data='{"kind": "medium machine"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'reconfigured Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'small' in rv.data)
        self.assertTrue(b'medium' in rv.data)
        # Secondary path (not found)
        rv = self.app.put('/v1/servers/srv002',
                          data='{"kind": "medium machine"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 404)
        # Secondary path (bad request)
        rv = self.app.put('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 400)

    def test_06_empty_processes(self):
        rv = self.app.get('/v1/servers/srv001/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'{}' in rv.data)
        # Secondary path (not found)
        rv = self.app.get('/v1/servers/srv002/processes')
        self.assertTrue(rv.status_code == 404)

    def test_07_create_process(self):
        rv = self.app.post('/v1/servers/srv001/processes/proc001',
                           data='{"kind": "tetris.exe"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'launched Ok' in rv.data)
        # Secondary path (conflict)
        rv = self.app.post('/v1/servers/srv001/processes/proc001',
                           data='{"kind": "pong.exe"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 409)
        # Secondary path (bad request)
        rv = self.app.post('/v1/servers/srv001/processes/proc002')
        self.assertTrue(rv.status_code == 400)

    def test_08_read_process(self):
        rv = self.app.get('/v1/servers/srv001/processes/proc001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)
        # Secondary path (not found)
        rv = self.app.get('/v1/servers/srv001/processes/proc002')
        self.assertTrue(rv.status_code == 404)

    def test_09_update_process(self):
        rv = self.app.put('/v1/servers/srv001/processes/proc001',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'modified Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pacman' in rv.data)
        # Secondary path (not found)
        rv = self.app.put('/v1/servers/srv001/processes/proc002',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 404)
        # Secondary path (bad request)
        rv = self.app.put('/v1/servers/srv001/processes/proc001')
        self.assertTrue(rv.status_code == 400)

    def test_10_filter_max_load(self):
        rv = self.app.post('/v1/servers/srv007',
                           data='{"kind": "large machine"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'started Ok' in rv.data)
        rv = self.app.post('/v1/servers/srv007/processes/proc001',
                           data='{"kind": "tetris.exe"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'launched Ok' in rv.data)
        rv = self.app.post('/v1/servers/srv007/processes/proc002',
                           data='{"kind": "pong.exe"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'launched Ok' in rv.data)
        rv = self.app.get('/v1/servers?filter=max_load')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv007' in rv.data)
        # Secondary path (graceful unknown filter)
        rv = self.app.get('/v1/servers?filter=unknown_filter')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)
        # Secondary path (graceful unknown query param)
        rv = self.app.get('/v1/servers?unknown_query=unknown_filter')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_11_read_servers(self):
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_12_read_processes(self):
        rv = self.app.get('/v1/servers/srv007/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)
        # Secondary path (not found)
        rv = self.app.get('/v1/servers/srv002/processes')
        self.assertTrue(rv.status_code == 404)

    def test_13_delete_process(self):
        rv = self.app.delete('/v1/servers/srv007/processes/proc001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'halted Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv007/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)
        # Secondary path (not found)
        rv = self.app.delete('/v1/servers/srv007/processes/proc001')
        self.assertTrue(rv.status_code == 404)
        # Secondary path (not found)
        rv = self.app.delete('/v1/servers/srv002/processes/proc001')
        self.assertTrue(rv.status_code == 404)

    def test_14_delete_server(self):
        rv = self.app.delete('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'stopped Ok' in rv.data)
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)
        # Secondary path (not found)
        rv = self.app.delete('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 404)


if __name__ == '__main__':
    unittest.main()
