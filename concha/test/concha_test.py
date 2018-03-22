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
import concha

GIVEN_OK = """
"given": {
    "root": {
        "form": "repite",
        "obj": {
            "form": "*algo"
        }
    }
}"""
THEN_OK = """
"then": {
    "200": "{d[root][obj]}",
    "400": "No puedo repetirlo, no me has especificado qué repetir"
}"""
THEN_WRONG = """
"then": {
    "200": "{d[root][wrong]}",
    "400": "No puedo repetirlo, no me has especificado qué repetir"
}"""
WHEN_WRONG = """
"when": {
    "method": "TREAT",
    "uri": "{d[root][wrong]}"
}"""
GIVEN_OK2 = """
"given": {
    "root": {
        "form": "expón",
        "obj": {
            "form": "*algo"
        }
    }
}"""
THEN_OK2 = """
"then": {
    "200": "{d[root][obj]}",
    "400": "No puedo exponerlo, no me has especificado qué exponer"
}"""


def create_trick(app, data_text=None):
    if data_text:
        return app.post(
            '/v1/tricks',
            data=data_text,
            mimetype='application/json')
    else:
        return app.post(
            '/v1/tricks')


class TricksResourceTestCase(unittest.TestCase):
    def setUp(self):
        concha.app.config['TESTING'] = True
        self.app = concha.app.test_client()

    def tearDown(self):
        concha.reset()

    def test_empty_tricks(self):
        rv = self.app.get('/v1/tricks')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'[]' in rv.data)

    def test_create_trick(self):
        rv = create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'created Ok' in rv.data)

    def test_create_trick_2ndp_bad_request_no_data(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = create_trick(self.app)

        self.assertTrue(rv.status_code == 400)

    def test_create_trick_2ndp_bad_request_no_then(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = create_trick(self.app, "{{{}}}".format(GIVEN_OK))

        self.assertTrue(rv.status_code == 400)

    def test_create_trick_2ndp_bad_request_wrong_then(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_WRONG))

        self.assertTrue(rv.status_code == 400)

    def test_create_trick_2ndp_bad_request_wrong_when(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = create_trick(self.app, "{{{}, {}, {}}}".format(GIVEN_OK, WHEN_WRONG, THEN_OK))

        self.assertTrue(rv.status_code == 400)

    def test_read_trick(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = self.app.get('/v1/tricks/0')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'"form": "repite"' in rv.data)

    def test_read_trick_2ndp_not_found(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = self.app.get('/v1/tricks/1')

        self.assertTrue(rv.status_code == 404)

    def test_update_trick(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = self.app.put(
            '/v1/tricks/0',
            data="{{{}, {}}}".format(GIVEN_OK2, THEN_OK2),
            mimetype='application/json')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'modified Ok' in rv.data)
        rv = self.app.get('/v1/tricks/0')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'exponer' in rv.data)

    def test_update_trick_2ndp_not_found(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = self.app.put(
            '/v1/tricks/1',
            data="{{{}, {}}}".format(GIVEN_OK2, THEN_OK2),
            mimetype='application/json')

        self.assertTrue(rv.status_code == 404)

    def test_read_tricks(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK2, THEN_OK2))

        rv = self.app.get('/v1/tricks')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'No puedo repetirlo' in rv.data)
        self.assertTrue(b'No puedo exponerlo' in rv.data)

    def test_delete_trick(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK2, THEN_OK2))

        rv = self.app.delete('/v1/tricks/1')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'deleted Ok' in rv.data)
        rv = self.app.get('/v1/tricks')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(b'No puedo exponerlo' in rv.data)
        self.assertTrue(b'No puedo repetirlo' in rv.data)

    def test_delete_trick_2ndp_not_found(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK2, THEN_OK2))

        rv = self.app.delete('/v1/tricks/2')

        self.assertTrue(rv.status_code == 404)


#   Monkey |  ´..`3 | Patches some internal calls out of testing paths.
# Patching | (-  )\ | No monkey was harmed in the process. """
def do_monkey_patching():
    global process_document_tmp
    process_document_tmp = concha.process_document
    concha.process_document = monkey_patching_process_document


def undo_monkey_patching():
    global process_document_tmp
    concha.process_document = process_document_tmp


def monkey_patching_process_document(_, __):
    return {
        "root": {
            "form": "repite",
            "id": 0,
            "obj": {
                    "form": "mock",
                    "id": 1
                }
            }
        }, 200


def post_document(app, data_text=None):
    if data_text:
        return app.post(
            '/v1/documents',
            data=data_text,
            mimetype='application/json')
    else:
        return app.post(
            '/v1/documents')


class DocumentsResourceTestCase(unittest.TestCase):
    def setUp(self):
        concha.app.config['TESTING'] = True
        self.app = concha.app.test_client()
        do_monkey_patching()

    def tearDown(self):
        undo_monkey_patching()
        concha.reset()

    def test_post_document(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = post_document(self.app, '{"text": "ignored"}')

        self.assertTrue(rv.status_code == 201)
        self.assertTrue(b'mock' in rv.data)

    def test_post_documents_2ndp_bad_request(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))

        rv = post_document(self.app)

        self.assertTrue(rv.status_code == 400)

    def test_get_documents(self):
        create_trick(self.app, "{{{}, {}}}".format(GIVEN_OK, THEN_OK))
        post_document(self.app, '{"text": "uno"}')
        post_document(self.app, '{"text": "dos"}')

        rv = self.app.get('/v1/documents')

        self.assertTrue(rv.status_code == 200)
        self.assertTrue(b'uno' in rv.data)
        self.assertTrue(b'dos' in rv.data)


if __name__ == '__main__':
    unittest.main()
