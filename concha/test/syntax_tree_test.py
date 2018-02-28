# -*- coding: utf-8 -*-
import unittest
import syntax_tree

a_tree_txt = '\
1	mi	_	DET	_	Number=Sing|Person=1|Poss=Yes|PronType=Prs|fPOS=det++	2	det	_	_\n\
2	mamá	_	noun	_	Gender=Fem|Number=Sing|fPOS=noun++	4	nsubj	_	_\n\
3	me	_	pron	_	Case=Acc,Dat|Number=Sing|Person=1|PrepCase=Npr|PronType=Prs|Reflex=Yes|fPOS=pron++	4	iobj	_	_\n\
4	mima	_	verb	_	Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|fPOS=verb++	0	root	_	_\n\
\n\
'

b_tree_txt = '\
1	la	_	det	_	Definite=Def|Gender=Fem|Number=Sing|PronType=Art|fPOS=det++	2	det	_	_\n\
2	señora	_	noun	_	Gender=Fem|Number=Sing|fPOS=noun++	0	root	_	_\n\
3	Concha	_	propn	_	fPOS=propn++	2	appos	_	_\n\
\n\
'


class SyntaxTreeTest(unittest.TestCase):

    def setUp(self):
        self.tree = syntax_tree.SyntaxTree()
        self.tree.parse_connl(a_tree_txt)

    def test_parse(self):
        self.assertTrue(self.tree['root']['form'] == 'mima')
        self.assertTrue(self.tree['root']['iobj']['form'] == 'me')
        self.assertTrue(self.tree['root']['nsubj']['form'] == 'mamá')
        self.assertTrue(self.tree['root']['nsubj']['det']['form'] == 'mi')

    def test_parse_fail(self):
        with self.assertRaises(syntax_tree.SyntaxTree.ParseError):
            bad_tree = syntax_tree.SyntaxTree()
            bad_tree.parse_connl('1	mi	_	DET	_	Number=Sing|Per')

    def test_deep_replacement(self):
        b_tree = syntax_tree.SyntaxTree()
        b_tree.parse_connl(b_tree_txt)
        threshold = self.tree['root']['nsubj'].max() + 1
        delta = b_tree['root'].len() - self.tree['root']['nsubj'].len()
        replaced_tree = self.tree.deep_replacement(self.tree['root'], 'nsubj', b_tree['root'], delta, threshold)
        self.assertTrue(replaced_tree['root']['nsubj']['appos']['form'] == 'Concha')
        self.assertTrue(replaced_tree['root']['nsubj']['appos']['id'] == '3')
        self.assertTrue(replaced_tree['root']['id'] == '5')

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

    def test_format(self):
        txt = '{root[nsubj]} es muy mimosa'.format_map(self.tree)
        self.assertTrue(txt == 'mi mamá es muy mimosa')


if __name__ == '__main__':
    unittest.main()
