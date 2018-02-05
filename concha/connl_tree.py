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
    'Branch', 'sub_tree', 'ParseError', 'ConnlTree', 'text_parse'
]

import subprocess
from functools import reduce
from collections import namedtuple

REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), \
        ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')
CONNL_KEYS = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG',
              'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
SUBTREE_KEYS = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'DEPS', 'MISC']

Branch = namedtuple('Branch', ['tree', 'parent', 'key'])


def sub_tree(tree, path):
    """Traverse a dict tree according to format() style providing the parent and the branch key."""
    key_list = path.translate({ord(c): None for c in '{]}'}).split('[')  # format() path to list
    parent, key = (None,)*2
    for key in key_list:
        parent = tree
        tree = tree[key]
    return Branch(tree=tree, parent=parent, key=key)


class ParseError(Exception):
    """Exception raised for errors in the parsing.

    Attributes:
        text -- input expression in which the parsing error occurred
        message -- explanation of the error
    """

    def __init__(self, text, message):
        self.text = text
        self.message = message


def _connl_tree_fill(index, tokens):
    """Recursively fulfill DEPREL relationships."""
    deprel = tokens[index]['DEPREL']
    subtree = ConnlTree()
    for i in SUBTREE_KEYS:
        if tokens[index][i] != '_':
            subtree.update({i: tokens[index][i]})
    for child_index in tokens[index]['children']:
        subtree.update(_connl_tree_fill(child_index, tokens))
    result = ConnlTree({deprel: subtree})
    return result


def _connl_format(tree):
    """Return a dict with all the dependant FORMs indexed by ID."""
    result = {int(tree['ID']): tree['FORM']}
    for key in tree:
        if key not in SUBTREE_KEYS:
            result.update(_connl_format(tree[key]))
    return result


class ConnlTree(dict):
    """Handle texts in nested tokens according to DEPREL relationships."""

#    def __init__(self, other=None, *arg, **kw):
#        """Create a dict+list structure out of a CoNNL text format."""
#        super(ConnlTree, self).__init__(*arg, **kw)

    def parse(self, connl_text):
        """Update inner dict structure out of a CoNNL text format."""
        try:
            connl_text = connl_text.rstrip()  # Removing unwanted ending '\n'.
            tokens = []
            root = None
            words = connl_text.split('\n')  # A word per line.
            for word in words:
                values = word.split('\t')  # A CoNLL field per tab.
                token = dict(zip(CONNL_KEYS, values))  # New Token with Key-Value joining.
                token['children'] = []  # Add an extra empty field for tree dependency reversing.
                if token['HEAD'] == '0':  # Identify ROOT index.
                    root = int(token['ID']) - 1
                tokens.append(token)  # Add k-v to the token list.
            for token in tokens:  # Reverse the tree dependencies fulfilling the children field.
                head_index = int(token['HEAD']) - 1
                if head_index >= 0:
                    tokens[head_index]['children'].append(int(token['ID']) - 1)
            tree = _connl_tree_fill(root, tokens)  # Recursive tree completion.
            self.update(tree)
        except Exception:
            raise ParseError(connl_text, 'The text was not CoNNL compliant.')
        return self

    def len(self):
        """Count how many nodes in a ConnlTree."""
        count = 1
        for key, value in self.items():
            if isinstance(value, ConnlTree):
                count += value.len()
        return count

    def min(self):
        """Find the minimum ID a (sub)ConnlTree."""
        n = int(self['ID'])
        for key, value in self.items():
            if isinstance(value, ConnlTree):
                n = min(n, value.min())
        return n

    def max(self):
        """Find the minimum ID a (sub)ConnlTree."""
        n = int(self['ID'])
        for key, value in self.items():
            if isinstance(value, ConnlTree):
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
            if isinstance(value, ConnlTree):
                value.renumber(delta, threshold)
            elif key == 'ID':
                id_ = int(value)
                if id_ >= threshold:
                    self.update({key: str(id_ + delta)})

    def deepcopy(self):
        """Creates a deep copy of self."""
        branch = ConnlTree()
        for key, value in self.items():
            if isinstance(value, ConnlTree):
                branch.update(ConnlTree({key: value.deepcopy()}))
            else:
                branch.update(ConnlTree({key: value}))
        return branch

    def deep_replacement(self, source_parent, source_key, replacement, delta, threshold):
        """Creates a deep copy of self replacing source branch."""
        branch = ConnlTree()
        for key, value in self.items():
            if isinstance(value, ConnlTree):
                if self == source_parent and key == source_key:
                    branch.update(ConnlTree({source_key: replacement}))
                else:
                    branch.update(ConnlTree({key: value.deep_replacement(
                        source_parent, source_key, replacement, delta, threshold
                    )}))
            elif key == 'ID':
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
                if key == 'FORM':
                    form_kind = tree['FORM'][0]
                    if form_kind == '*':  # Any.
                        tree_matches &= True
                    elif form_kind == '~':  # Similar. TODO: search for embeddings
                        tree_matches &= self['FORM'] == tree['FORM'][1:]
                    else:  # Equal.
                        tree_matches &= self['FORM'] == tree['FORM']
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
        """Format a ConnlTree object for string.format() focusing on ordered 'FORM' fields."""
        forms = _connl_format(self)
        return ' '.join(str(forms[key]) for key in sorted(forms))


def text_parse(text):
    """Do a external parsing returning it in a CoNNL tree. It can evolve to other invocation ways"""
    text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
    shell_cmd = 'echo ' + text + ' | ./parse.sh ../lang_models/Spanish'
    connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
    connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
    result = ConnlTree()
    return result.parse(connl_txt)
