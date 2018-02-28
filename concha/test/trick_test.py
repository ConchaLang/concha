# -*- coding: utf-8 -*-
import unittest
from trick import append_trick, match_tricks, default_domain  # expand_trick,
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

    def test_append_trick(self):
        domain = []
        append_trick(a_trick, domain)
        append_trick(a_trick)
        self.assertTrue(
            domain[0] == default_domain[0] and
            len(domain) == len(default_domain)
        )

    def test_match_tricks(self):
        domain = []
        append_trick(a_trick, domain)
        append_trick(b_trick, domain)
        tree = SyntaxTree()
        tree.parse_connl(a_tree_txt)
        matched_tricks = match_tricks(tree, domain)
        self.assertTrue(
            len(matched_tricks) == 1 and
            domain[0]['given']['root']['iobj']['form'] == '*alguien'
        )


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
