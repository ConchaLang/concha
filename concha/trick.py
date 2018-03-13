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
    'TrickError', 'append_trick', 'match_tricks', 'default_domain', 'error_domain', 'syntactic_trick_errors'
]

from syntax_tree import SyntaxTree
import re


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


def match_tricks(tree: SyntaxTree, trick_domain=default_domain):
    """Identify th eindexes of which tricks matches with provided CoNNL tree document."""
    candidates = []
    for i, trick in enumerate(trick_domain):
        if tree.matches(trick['given']):
            candidates.append(i)
    return candidates


def syntactic_trick_errors(trick):
    """Verify trick structure and if 'when' and 'then' parts match in the document usage ({d[...]})"""
    result = []
    if 'given' in trick and 'then' in trick:
        d = {'d': trick['given']}
        for k, v in trick['then'].items():
            expressions = re.findall('\{d.*?\}',v)
            for e in expressions:
                try:
                    x = e.format_map(d)
                except Exception as exception:
                    result.append('Wrong construct in "then" part coded "{}": "{}"'.format(k, exception))
        if 'when' in trick:
            expressions = re.findall('\{d.*?\}',trick['when']['uri'])
            for e in expressions:
                try:
                    x = e.format_map(d)
                except Exception as exception:
                    result.append('Wrong construct in "when" part: "{}"'.format(exception))
    else:
        result.append('Wrong trick construct: missing "given" or "then" part')
    return result
