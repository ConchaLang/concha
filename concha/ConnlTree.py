# -*- coding: utf-8 -*-

CONNL_KEYS = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
SUBTREE_KEYS = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'DEPS', 'MISC']


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
    """ Recursively fulfill deprel relationships. """
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
    """ Returns a dict with all the dependant FORMs indexed by ID. """
    result = {tree['ID']: tree['FORM']}
    for key in tree:
        if key not in SUBTREE_KEYS:
            result.update(_connl_format(tree[key]))
    return result


class ConnlTree(dict):
    """ Handles texts in nested tokens according to separators """

#    def __init__(self, other=None, *arg, **kw):
#        """ Creates a dict+list structure out of a CoNNL text format. """
#        super(ConnlTree, self).__init__(*arg, **kw)

    def parse(self, connl_text):
        """ Updates inner dict structure out of a CoNNL text format. """
        tree = None
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
        except Exception:
            raise ParseError(connl_text, 'The text was not CoNNL compliant.' )
        self.update(tree)
        return self

    def matches(self, tree):
        """ Returns if self is equal or similar to a dict tree, which can be a pattern. """
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
        """ Does the string formatting of a ConnlTree object focusing on ordered 'FORM' fields. """
        forms = _connl_format(self)
        return ' '.join(str(forms[key]) for key in sorted(forms))
