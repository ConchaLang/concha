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

    def test_02_create_server(self):
        rv = self.app.post('/v1/servers/srv001',
                           data='{"kind": "small machine"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'started Ok' in rv.data)

    def test_03_read_server(self):
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)

    def test_04_update_server(self):
        rv = self.app.put('/v1/servers/srv001',
                          data='{"kind": "medium machine"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'reconfigured Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'small' in rv.data)
        self.assertTrue(b'medium' in rv.data)

    def test_05_empty_processes(self):
        rv = self.app.get('/v1/servers/srv001/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'{}' in rv.data)

    def test_06_create_process(self):
        rv = self.app.post('/v1/servers/srv001/processes/proc001',
                           data='{"kind": "tetris.exe"}',
                           mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'launched Ok' in rv.data)

    def test_07_read_process(self):
        rv = self.app.get('/v1/servers/srv001/processes/proc001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)

    def test_08_update_process(self):
        rv = self.app.put('/v1/servers/srv001/processes/proc001',
                          data='{"kind": "pacman.exe"}',
                          mimetype='application/json')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'modified Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pacman' in rv.data)

    def test_09_filter_max_load(self):
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

    def test_10_read_servers(self):
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)

    def test_11_read_processes(self):
        rv = self.app.get('/v1/servers/srv007/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)

    def test_12_delete_process(self):
        rv = self.app.delete('/v1/servers/srv007/processes/proc001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'halted Ok' in rv.data)
        rv = self.app.get('/v1/servers/srv007/processes')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'tetris' in rv.data)
        self.assertTrue(b'pong' in rv.data)

    def test_13_delete_server(self):
        rv = self.app.delete('/v1/servers/srv001')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'stopped Ok' in rv.data)
        rv = self.app.get('/v1/servers')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'srv001' in rv.data)
        self.assertTrue(b'srv007' in rv.data)


if __name__ == '__main__':
    unittest.main()
