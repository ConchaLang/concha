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
__all__ = [
    'TrickError', 'append_trick', 'expand_trick', 'match_tricks', 'default_domain', 'error_domain'
]

import json
from connl_tree import text_parse


class TrickError(Exception):
    """Exception raised for errors in the trick handling.

    Attributes:
        trick -- object in which the trick failure occurred
        message -- explanation of the error
    """

    def __init__(self, trick, message):
        self.trick = trick
        self.message = message


default_domain = []
error_domain = []


def append_trick(trick, trick_domain=default_domain):
    if 'when' in trick:
        if 'method' in trick['when']:
            if trick['when']['method'] == 'ERROR':
                trick_domain = error_domain
    trick_domain.append(trick)


def expand_trick(trick, doc):
    """Substitute the 'then' part of a trick according to a document."""
    context = {'d': doc}
    status_code = None
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
        elif trick['when']['method'] == 'TREAT':
            uri = trick['when']['uri'].format_map(context)
            doc = text_parse(uri)
            link(doc, tricks)  # TODO *****************
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


def match_tricks(tree, trick_domain=default_domain):
    """Identify th eindexes of which tricks matches with provided CoNNL tree document."""
    candidates = []
    for i, trick in enumerate(trick_domain):
        if tree.matches(trick['given']):
            candidates.append(i)
    return candidates
