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
import syntax_tree

a_connl_tree_txt = '\
1	mi	_	DET	_	Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=det++	2	det	_	_\n\
2	mamá	_	noun	_	Gender=Fem|Number=Sing|fPOS=noun++	4	nsubj	_	_\n\
3	me	_	pron	_	Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=pron++	4	iobj	_	_\n\
4	mima	_	verb	_	Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=verb++	0	root	_	_\n\
\n\
'

b_connl_tree_txt = '\
1	la	_	det	_	Definite=Def|Gender=Fem|Number=Sing|PronType=Art|fPOS=det++	2	det	_	_\n\
2	señora	_	noun	_	Gender=Fem|Number=Sing|fPOS=noun++	0	root	_	_\n\
3	Concha	_	propn	_	fPOS=propn++	2	appos	_	_\n\
\n\
'

a_gcnl_tree = {
    "sentences": [
        {
            "text": {
                "content": "mi mamá me mima",
                "beginOffset": 0,
            },
            "sentiment": {
                "magnitude": 0,
                "score": 0,
            },
        }
    ],
    "tokens": [
        {
            "text": {
                "content": "mi",
                "beginOffset": 0,
            },
            "partOfSpeech": {
                "Number": "Sing",
                "Person": "1",
                "Poss": "Yes",
                "PronType": "Prs",
                "fPOS": "det++",
            },
            "dependencyEdge": {
                "headTokenIndex": 1,
                "label": "det",
            },
            "lemma": ""
        },
        {
            "text": {
                "content": "mamá",
                "beginOffset": 3,
            },
            "partOfSpeech": {
                "Gender": "Fem",
                "Number": "Sing",
                "fPOS": "noun++",
            },
            "dependencyEdge": {
                "headTokenIndex": 3,
                "label": "nsubj",
            },
            "lemma": ""
        },
        {
            "text": {
                "content": "me",
                "beginOffset": 8,
            },
            "partOfSpeech": {
                "Case": "Acc,Dat",
                "Number": "Sing",
                "Person": "1",
                "PrepCase": "Npr",
                "PronType": "Prs",
                "Reflex": "Yes",
                "fPOS": "pron++",
            },
            "dependencyEdge": {
                "headTokenIndex": 3,
                "label": "iobj",
            },
            "lemma": ""
        },
        {
            "text": {
                "content": "mima",
                "beginOffset": 13,
            },
            "partOfSpeech": {
                "Mood": "Ind",
                "Number": "Sing",
                "Person": "1",
                "Tense": "Past",
                "VerbForm": "Fin",
                "fPOS": "verb++",
            },
            "dependencyEdge": {
                "headTokenIndex": 3,
                "label": "root",
            },
            "lemma": ""
        }
    ],
    "language": "es"
}

# new_from_text is intentionally not unitary tested due its external dependencies.


class SyntaxTreeConnlTest(unittest.TestCase):

    def setUp(self):
        self.tree = syntax_tree.SyntaxTree()
        self.tree.parse_connl(a_connl_tree_txt)

    def test_parse(self):
        self.assertTrue(self.tree['root']['form'] == 'mima')
        self.assertTrue(self.tree['root']['iobj']['form'] == 'me')
        self.assertTrue(self.tree['root']['nsubj']['form'] == 'mamá')
        self.assertTrue(self.tree['root']['nsubj']['det']['form'] == 'mi')

    def test_parse_fail(self):
        with self.assertRaises(syntax_tree.SyntaxTree.SyntaxError):
            bad_tree = syntax_tree.SyntaxTree()
            bad_tree.parse_connl('1	mi	_	DET	_	Number=Sing|Per')


class SyntaxTreeGcnlTest(unittest.TestCase):

    def setUp(self):
        self.tree = syntax_tree.SyntaxTree()
        self.tree.parse_gcnl(a_gcnl_tree)

    def test_parse(self):
        self.assertTrue(self.tree['root']['form'] == 'mima')
        self.assertTrue(self.tree['root']['iobj']['form'] == 'me')
        self.assertTrue(self.tree['root']['nsubj']['form'] == 'mamá')
        self.assertTrue(self.tree['root']['nsubj']['det']['form'] == 'mi')

    def test_parse_fail(self):
        with self.assertRaises(syntax_tree.SyntaxTree.SyntaxError):
            bad_tree = syntax_tree.SyntaxTree()
            bad_tree.parse_connl('1	mi	_	DET	_	Number=Sing|Per')


class SyntaxTreeMatchingTest(unittest.TestCase):

    def setUp(self):
        self.tree = syntax_tree.SyntaxTree()
        self.tree.parse_gcnl(a_gcnl_tree)

    def test_point_to_content(self):
        context = {'d': self.tree}
        pointed = syntax_tree.SyntaxTree.point_to_content(context, 'd[root][iobj]')
        self.assertTrue(pointed['form'] == 'me')

    def test_point_to_content_2ndp_not_found(self):
        context = {'d': self.tree}
        with self.assertRaises(syntax_tree.SyntaxTree.SyntaxError):
            syntax_tree.SyntaxTree.point_to_content(context, 'd[root][wrong]')

    def test_deepcopy(self):
        self.assertTrue(self.tree.deepcopy()['root']['form'] == 'mima')

    def test_match(self):
        self.assertTrue(self.tree.matches({'root': {'form': 'mima', 'iobj': {'form': 'me'}}}))
        self.assertTrue(self.tree.matches({'root': {'form': 'mima', 'iobj': {'form': '~me'}}}))
        self.assertTrue(self.tree.matches({'root': {'form': 'mima', 'iobj': {'form': '*cosa'}}}))

    def test_match_fail(self):
        self.assertFalse(
            self.tree.matches({'root': {'form': 'mima', 'dobj': {'form': 'cosa'}}}) or
            self.tree.matches({'root': {'form': 'mima', 'iobj': {'form': 'cosa'}}}) or
            self.tree.matches({'root': {'form': 'mima', 'iobj': {'form': '~cosa'}}})
        )

    def test_to_string_replacing(self):
        context = {'d': self.tree}
        pointed = syntax_tree.SyntaxTree.point_to_content(context, 'd[root][iobj]')
        self.assertTrue(self.tree.to_string_replacing(pointed, 'te') == 'mi mamá te mima')

    def test_format(self):
        txt = '{root[nsubj]} es muy mimosa'.format_map(self.tree)
        self.assertTrue(txt == 'mi mamá es muy mimosa')

    def test_format_2ndp_not_found(self):
        with self.assertRaises(KeyError):
            '{root[wrong]} es muy mimosa'.format_map(self.tree)


if __name__ == '__main__':
    unittest.main()
