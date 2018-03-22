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
import trick
from syntax_tree import SyntaxTree

a_tree_txt = '\
1	mi	_	det	_	Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=det++	2	det	_	_\n\
2	mamá	_	noun	_	Gender=Fem|Number=Sing|fPOS=noun++	4	nsubj	_	_\n\
3	me	_	pron	_	Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=pron++	4	iobj	_	_\n\
4	mima	_	verb	_	Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=verb++	0	root	_	_\n\
\n\
'

a_trick = {
    "given": {
        "root": {
            "form": "mima",
            "iobj": {
                "form": "*alguien"
            }
        }
    },
    "then": {
        "200": "{d[root][iobj]}",
        "400": "Algo va mal"
    }
}

b_trick = {
    "given": {
        "root": {
            "form": "mina",
            "dobj": {
                "form": "*alguien"
            }
        }
    },
    "when": {
        "method": "PAST",
    },
    "then": {
        "200": "{d[root][dobj]}",
        "400": "Algo va mal"
    }
}


class TrickTest(unittest.TestCase):

    def setUp(self):
        self.domain = []

    def tearDown(self):
        trick.reset()

    def test_append_trick(self):
        trick.append_trick(a_trick, self.domain)
        trick.append_trick(a_trick)
        self.assertTrue(self.domain[0] == trick.default_domain[0])
        self.assertTrue(len(self.domain) == len(trick.default_domain))

    def test_match_tricks(self):
        trick.append_trick(a_trick, self.domain)
        trick.append_trick(b_trick, self.domain)
        tree = SyntaxTree()
        tree.parse_connl(a_tree_txt)
        matched_tricks = trick.match_tricks(tree, self.domain)
        self.assertTrue(len(matched_tricks) == 1)
        self.assertTrue(self.domain[0]['given']['root']['iobj']['form'] == '*alguien')


if __name__ == '__main__':
    unittest.main()


"""
    def test_expand_trick(self):
        tree = SyntaxTree()
        tree.parse_connl(a_tree_txt)
        self.assertTrue(
            expand_trick(a_trick, tree) == 'me' and
            expand_trick(b_trick, tree) == 'Algo va mal'
        )
"""
