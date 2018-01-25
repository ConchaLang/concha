# -*- coding: utf-8 -*-
import unittest
import connl_tree

a_tree_txt = '\
1	mi	_	DET	_	Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=DET++	2	det	_	_\n\
2	mamá	_	NOUN	_	Gender=Fem|Number=Sing|fPOS=NOUN++	4	nsubj	_	_\n\
3	me	_	PRON	_	Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=PRON++	4	iobj	_	_\n\
4	mima	_	VERB	_	Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=VERB++	0	ROOT	_	_\n\
\n\
'

a_tree = {
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


class ConnlTreeTest(unittest.TestCase):

    def setUp(self):
        self.tree = connl_tree.ConnlTree()
        self.tree.parse(a_tree_txt)

    def test_parse(self):
        self.assertTrue(
            self.tree['ROOT']['FORM'] == 'mima' and
            self.tree['ROOT']['iobj']['FORM'] == 'me' and
            self.tree['ROOT']['nsubj']['FORM'] == 'mamá' and
            self.tree['ROOT']['nsubj']['det']['FORM'] == 'mi'
        )

    def test_parse_fail(self):
        with self.assertRaises(connl_tree.ParseError):
            bad_tree = connl_tree.ConnlTree()
            bad_tree.parse('1	mi	_	DET	_	Number=Sing|Per')

    def test_match(self):
        self.assertTrue(
            self.tree.matches({'ROOT': {'FORM': 'mima', 'iobj': {'FORM': 'me'}}}) and
            self.tree.matches({'ROOT': {'FORM': 'mima', 'iobj': {'FORM': '~me'}}}) and
            self.tree.matches({'ROOT': {'FORM': 'mima', 'iobj': {'FORM': '*cosa'}}})
        )

    def test_match_fail(self):
        self.assertFalse(
            self.tree.matches({'ROOT': {'FORM': 'mima', 'dobj': {'FORM': 'cosa'}}}) or
            self.tree.matches({'ROOT': {'FORM': 'mima', 'iobj': {'FORM': 'cosa'}}}) or
            self.tree.matches({'ROOT': {'FORM': 'mima', 'iobj': {'FORM': '~cosa'}}})
        )

    def test_format(self):
        txt = '{ROOT[nsubj]} es muy mimosa'.format_map(self.tree)
        self.assertTrue(
            txt == 'mi mamá es muy mimosa'
        )


if __name__ == '__main__':
    unittest.main()
