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
    'Branch', 'sub_tree', 'SyntaxTree',
]

import subprocess
import requests
import json
from functools import reduce
from ast import literal_eval
from collections import namedtuple

REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), \
        ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')
REPL2 = ('=', '": "'), ('|', '", "')
CONNL_KEYS = ['id', 'form', 'lemma', 'upostag', 'xpostag',
              'feats', 'head', 'deprel', 'deps', 'misc']
SUBTREE_KEYS = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'deps', 'misc']

Branch = namedtuple('Branch', ['tree', 'parent', 'key'])


def sub_tree(tree, path):
    """Traverse a dict tree according to format() style providing the parent and the branch key."""
    key_list = path.translate({ord(c): None for c in '{]}'}).split('[')  # format() path to list
    parent, key = (None,)*2
    for key in key_list:
        parent = tree
        tree = tree[key]
    return Branch(tree=tree, parent=parent, key=key)


class SyntaxTree(dict):
    """Handle texts in nested tokens according to DEPREL relationships."""

#    def __init__(self, other=None, *arg, **kw):
#        """Create a dict+list structure out of a CoNNL text format."""
#        super(SyntaxTree, self).__init__(*arg, **kw)

    @staticmethod
    def new_from_text(text, shell_method=False):
        new = SyntaxTree()
        if shell_method:  # TODO DEPRECATED
            """Do a slow Syntaxnet UniversalParsey parsing returning its connl text output in a CoNNL tree."""
            text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
            shell_cmd = 'echo "' + text + '" | ./parse.sh ../lang_models/Spanish'
            connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
            connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
            new.parse_connl(connl_txt)
        else:
            uri = 'http://localhost:7000/v1/documents:analyzeSyntax'  # TODO generalize
            response = requests.post(
                url=uri,
                json={
                    "document": {
                        "type": "PLAIN_TEXT",
                        "language": "es",
                        "content": text
                    },
                    "encodingType": "UTF8"
                }
            )
            if response.status_code == 200 and 'json' in response.headers['content-type']:
                new.parse_gcnl(json.loads(response.text))
            return new

    def parse_gcnl(self, gcnl_json):
        """Update inner dict structure out of a Google Cloud Natural Language syntax format."""
        try:
            root = None
            for idx, token in enumerate(gcnl_json['tokens']):  # Reverse tree dependencies adding the children field.
                head_index = token['dependencyEdge']['headTokenIndex']
                if 'children' not in token:  # Extra field for tree dependency reversing.
                    token['children'] = []
                if head_index == idx:  # Identify ROOT index.
                    root = idx
                elif 'children' in gcnl_json['tokens'][head_index]:  # Not in ROOT
                        gcnl_json['tokens'][head_index]['children'].append(idx)
                else:
                    gcnl_json['tokens'][head_index]['children'] = [idx]
            tree = SyntaxTree._fill_gcnl(root, gcnl_json['tokens'])  # Recursive tree completion.
            self.update(tree)
        except Exception:
            raise SyntaxTree.ParseError(gcnl_json, 'The json was not Google compliant.')
        return self

    def parse_connl(self, connl_tabular_text):
        """Update inner dict structure out of a CoNNL text format."""
        try:
            connl_tabular_text = connl_tabular_text.rstrip()  # Removing unwanted ending '\n'.
            tokens = []
            root = None
            words = connl_tabular_text.split('\n')  # A word per line.
            for word in words:
                values = word.split('\t')  # A CoNLL field per tab.
                token = dict(zip(CONNL_KEYS, values))  # New Token with Key-Value joining.
                token['children'] = []  # Add an extra empty field for tree dependency reversing.
                if token['head'] == '0':  # Identify ROOT index.
                    token['deprel'] = 'root'
                    root = int(token['id']) - 1
                token['feats'] = literal_eval('{{"{}"}}'.format(
                    reduce(lambda a, kv: a.replace(*kv), REPL2, token['feats'])
                ))
                tokens.append(token)  # Add k-v to the token list.
            for token in tokens:  # Reverse the tree dependencies fulfilling the children field.
                head_index = int(token['head']) - 1
                if head_index >= 0:
                    tokens[head_index]['children'].append(int(token['id']) - 1)
            tree = SyntaxTree._fill_connl(root, tokens)  # Recursive tree completion.
            self.update(tree)
        except Exception:
            raise SyntaxTree.ParseError(connl_tabular_text, 'The text was not CoNNL compliant.')
        return self

    @staticmethod
    def _fill_connl(index, tokens):
        """Recursively fulfill DEPREL relationships."""
        label = tokens[index]['deprel']
        subtree = SyntaxTree()
        for i in SUBTREE_KEYS:
            if tokens[index][i] != '_':
                subtree.update({i: tokens[index][i]})
        for child_index in tokens[index]['children']:
            subtree.update(SyntaxTree._fill_connl(child_index, tokens))
        result = SyntaxTree({label: subtree})
        return result

    @staticmethod
    def _fill_gcnl(index, tokens):
        """Recursively fulfill dependencyEdge relationships."""
        label = tokens[index]['dependencyEdge']['label']
        subtree = SyntaxTree()
        subtree.update({'id': index})
        subtree.update({'form': tokens[index]['text']['content']})
        subtree.update({'lemma': tokens[index]['lemma']})
        if 'fPOS' in tokens[index]['partOfSpeech']:
            subtree.update({'upostag': tokens[index]['partOfSpeech']['fPOS'].rstrip('+')})
        elif 'tag' in tokens[index]['partOfSpeech']:
            subtree.update({'upostag': tokens[index]['partOfSpeech']['tag']})
        subtree.update({'feats': tokens[index]['partOfSpeech']})
        for child_index in tokens[index]['children']:
            subtree.update(SyntaxTree._fill_gcnl(child_index, tokens))
        result = SyntaxTree({label: subtree})
        return result

    @staticmethod
    def _format(tree):
        """Return a dict with all the dependant FORMs indexed by ID."""
        result = {int(tree['id']): tree['form']}
        for key in tree:
            if key not in SUBTREE_KEYS:
                result.update(SyntaxTree._format(tree[key]))
        return result

    def len(self):
        """Count how many nodes in a SyntaxTree."""
        count = 1
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                count += value.len()
        return count

    def min(self):
        """Find the minimum ID a (sub)SyntaxTree."""
        n = int(self['id'])
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                n = min(n, value.min())
        return n

    def max(self):
        """Find the maximum ID a (sub)SyntaxTree."""
        n = int(self['id'])
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                n = max(n, value.max())
        return n

    def renumber(self, delta, threshold=0):
        """           threshold = max(source[grp]) + 1
        source  [grp] |        --> replacement
        1,2,3,4,(5,6),7,8,9,10 --> (1,2,3)
        0,0,0,0,(   ),1,1,1, 1 --> (4,4,4)
                      |             |
                      |             delta = min(source[grp]) - 1
                      delta = len(replacement) - len(source[grp])
        """
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                value.renumber(delta, threshold)
            elif key == 'id':
                id_ = int(value)
                if id_ >= threshold:
                    self.update({key: str(id_ + delta)})

    def deepcopy(self):
        """Creates a deep copy of self."""
        branch = SyntaxTree()
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                branch.update(SyntaxTree({key: value.deepcopy()}))
            else:
                branch.update(SyntaxTree({key: value}))
        return branch

    def deep_replacement(self, source_parent, source_key, replacement, delta, threshold):
        """Creates a deep copy of self replacing source branch."""
        branch = SyntaxTree()
        for key, value in self.items():
            if isinstance(value, SyntaxTree):
                if self == source_parent and key == source_key:
                    branch.update(SyntaxTree({source_key: replacement}))
                else:
                    branch.update(SyntaxTree({key: value.deep_replacement(
                        source_parent, source_key, replacement, delta, threshold
                    )}))
            elif key == 'id':
                id_ = int(value)
                if id_ >= threshold:
                    branch.update({key: str(id_ + delta)})
                else:
                    branch.update({key: value})
            else:
                branch.update({key: value})
        return branch

    def matches(self, tree):
        """Return if self is equal or similar to a dict tree, which can be a pattern."""
        tree_matches = True
        for key in tree:
            if key in self:
                if key == 'form':
                    form_kind = tree['form'][0]
                    if form_kind == '*':  # Any.
                        tree_matches &= True
                    elif form_kind == '~':  # Similar. TODO: search for embeddings
                        tree_matches &= self['form'] == tree['form'][1:]
                    else:  # Equal.
                        tree_matches &= self['form'] == tree['form']
                else:
                    a = self[key]
                    b = tree[key]
                    tree_matches &= a.matches(b)
            else:
                return False
            if not tree_matches:
                break
        return tree_matches

    def __format__(self, format_spec=None):
        """Format a SyntaxTree object for string.format() focusing on ordered 'FORM' fields."""
        forms = SyntaxTree._format(self)
        return ' '.join(str(forms[key]) for key in sorted(forms))

    class ParseError(Exception):
        """Exception raised for errors in the parsing.

        Attributes:
            text -- input expression in which the parsing error occurred
            message -- explanation of the error
        """

        def __init__(self, text, message):
            self.text = text
            self.message = message
