# -*- coding: utf-8 -*-
import unittest
from trick import append_trick, expand_trick, match_tricks, default_domain
from connl_tree import ConnlTree

a_tree_txt = '\
1	mi	_	DET	_	Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=DET++	2	det	_	_\n\
2	mamá	_	NOUN	_	Gender=Fem|Number=Sing|fPOS=NOUN++	4	nsubj	_	_\n\
3	me	_	PRON	_	Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=PRON++	4	iobj	_	_\n\
4	mima	_	VERB	_	Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=VERB++	0	ROOT	_	_\n\
\n\
'

a_doc = {
    "ROOT": {
        "FEATS": "Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=VERB++",
        "FORM": "mima",
        "ID": "4",
        "UPOSTAG": "VERB",
        "iobj": {
            "FEATS": "Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=PRON++",
            "FORM": "me",
            "ID": "3",
            "UPOSTAG": "PRON"
        },
        "nsubj": {
            "FEATS": "Gender=Fem|Number=Sing|fPOS=NOUN++",
            "FORM": "mamá",
            "ID": "2",
            "UPOSTAG": "NOUN",
            "det": {
                "FEATS": "Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=DET++",
                "FORM": "mi",
                "ID": "1",
                "UPOSTAG": "DET"
            }
        }
    }
}

a_trick = {
    "given": {
        "ROOT": {
            "FORM": "mima",
            "iobj": {
                "FORM": "*alguien"
            }
        }
    },
    "then": {
        "200": "{d[ROOT][iobj]}",
        "400": "Algo va mal"
    }
}

b_trick = {
    "given": {
        "ROOT": {
            "FORM": "mina",
            "dobj": {
                "FORM": "*alguien"
            }
        }
    },
    "when": {
        "method": "PAST",
    },
    "then": {
        "200": "{d[ROOT][dobj]}",
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

    def test_expand_trick(self):
        tree = ConnlTree()
        tree.parse(a_tree_txt)
        self.assertTrue(
            expand_trick(a_trick, tree) == 'me' and
            expand_trick(b_trick, tree) == 'Algo va mal'
        )

    def test_match_tricks(self):
        domain = []
        append_trick(a_trick, domain)
        tree = ConnlTree()
        tree.parse(a_tree_txt)
        matched_tricks = match_tricks(tree, domain)
        self.assertTrue(
            matched_tricks[0]['given']['ROOT']['iobj']['FORM'] == '*alguien'
        )


if __name__ == '__main__':
    unittest.main()
