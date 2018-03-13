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

import concha
import unittest


class ConchaTestCase(unittest.TestCase):
    def setUp(self):
        concha.app.config['TESTING'] = True
        self.app = concha.app.test_client()

    def test_01_empty_tricks(self):
        rv = self.app.get('/v1/tricks')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'[]' in rv.data)

    def test_02_create_trick(self):
        rv = self.app.post(
            '/v1/tricks',
            data="""{
                    "given": {
                        "root": {
                            "form": "repite",
                            "obj": {
                                "form": "*algo"
                            }
                        }
                    },
                    "then": {
                        "200": "{d[root][obj]}",
                        "400": "No puedo repetirlo, no me has especificado qué repetir"
                    }
                }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'created Ok' in rv.data)
        # Secondary path (bad request - no json)
        rv = self.app.post('/v1/tricks')
        self.assertTrue(rv.status_code == 400)
        # Secondary path (bad request - no then part)
        rv = self.app.post(
            '/v1/tricks',
            data="""{
                    "given": {
                        "root": {
                            "form": "repite",
                            "obj": {
                                "form": "*algo"
                            }
                        }
                    }
                }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 400)
        # Secondary path (bad request - wrong then)
        rv = self.app.post(
            '/v1/tricks',
            data="""{
                    "given": {
                        "root": {
                            "form": "repite",
                            "obj": {
                                "form": "*algo"
                            }
                        }
                    },
                    "then": {
                        "200": "{d[root][wrong]}",
                        "400": "No puedo repetirlo, no me has especificado qué repetir"
                    }
                }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 400)
        # Secondary path (bad request - wrong when)
        rv = self.app.post(
            '/v1/tricks',
            data="""{
                "given": {
                    "root": {
                        "form": "*haz",
                        "obj": {
                            "form": "*algo"
                        }
                    }
                },
                "when": {
                    "method": "TREAT",
                    "uri": "{d[root][wrong]}"
                },
                "then": {
                    "200": "{r[root]}"
                }
            }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 400)

    def test_03_read_trick(self):
        rv = self.app.get('/v1/tricks/0')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'"form": "repite"' in rv.data)
        # Secondary path (not found)
        rv = self.app.get('/v1/tricks/1')
        self.assertTrue(rv.status_code == 404)

    def test_04_update_trick(self):
        rv = self.app.put(
            '/v1/tricks/0',
            data="""{
                    "given": {
                        "root": {
                            "form": "repite",
                            "obj": {
                                "form": "*algo"
                            }
                        }
                    },
                    "then": {
                        "200": "{d[root][obj]}",
                        "400": "No puedo repetirlo, no me has indicado qué repetir"
                    }
                }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'modified Ok' in rv.data)
        rv = self.app.get('/v1/tricks/0')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'indicado' in rv.data)
        # Secondary path (not found)
        rv = self.app.put('/v1/tricks/1')
        self.assertTrue(rv.status_code == 404)

    def test_05_read_tricks(self):
        rv = self.app.post(
            '/v1/tricks',
            data="""{
                    "given": {
                        "root": {
                            "form": "expón",
                            "obj": {
                                "form": "*algo"
                            }
                        }
                    },
                    "then": {
                        "200": "Señores, quería exponerles algo relativo a {d[root][obj]}, si no les importa",
                        "400": "No puedo exponerlo, no me has especificado qué exponer"
                    }
                }""",
            mimetype='application/json')
        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'created Ok' in rv.data)
        rv = self.app.get('/v1/tricks')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'No puedo repetirlo' in rv.data)
        self.assertTrue(b'No puedo exponerlo' in rv.data)

    def test_06_delete_trick(self):
        rv = self.app.delete('/v1/tricks/1')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'deleted Ok' in rv.data)
        rv = self.app.get('/v1/tricks')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'No puedo exponerlo' in rv.data)
        self.assertTrue(b'No puedo repetirlo' in rv.data)
        # Secondary path (not found)
        rv = self.app.delete('/v1/tricks/1')
        self.assertTrue(rv.status_code == 404)


if __name__ == '__main__':
    unittest.main()
