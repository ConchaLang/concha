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
    'TrickError', 'append_trick', 'match_tricks', 'default_domain', 'error_domain', 'validate_trick'
]

from syntax_tree import SyntaxTree


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


def validate_trick(trick):
    """Verify if when and then parts matches with given tree branches"""
    # TODO (beware with the response substitutions {r[...][...]})
    return True
