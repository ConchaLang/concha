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
    'parse', 'link'
]

import subprocess
from connl_tree import ConnlTree
from functools import reduce
from random import choice
from collections import namedtuple
from trick import expand_trick, match_tricks, error_domain

TreatedDoc = namedtuple('TreatedDoc', ['treat', 'tricks', 'status'])
REPLS = ('.', ' . '), (',', ' , '), (';', ' ; '), (':', ' : '), ('¿', ' ¿ '), ('?', ' ? '), ('¡', ' ¡ '), ('!', ' ! ')


def parse(text):
    """Do a external parsing returning it in a CoNNL tree. It can evolve to other invocation ways"""
    text = reduce(lambda a, kv: a.replace(*kv), REPLS, text)  # Tokenize punctuation symbols
    shell_cmd = 'echo ' + text + ' | ./parse.sh ../lang_models/Spanish'
    connl_bin_output = subprocess.check_output([shell_cmd], shell=True)
    connl_txt = connl_bin_output.decode('utf-8')  # From Binary to String
    result = ConnlTree()
    return result.parse(connl_txt)


def link(doc, tricks):
    """return the doc modified according to a given trick domain."""
    expanded_trick, chosen_trick = (None,)*2
    candidate_tricks = match_tricks(doc, tricks)
    if len(candidate_tricks) > 0:
        chosen_trick = choice(candidate_tricks)
        expanded_trick = expand_trick(chosen_trick, doc)
        status = 201
    elif len(error_domain) > 0:
        candidate_tricks = match_tricks(doc, error_domain)
        chosen_trick = choice(candidate_tricks)
        expanded_trick = expand_trick(chosen_trick, doc)
        status = 404
    else:  # Fallback in English
        expanded_trick = 'No trick'
        status = 404
    return TreatedDoc(treat=expanded_trick, tricks=chosen_trick, status=status)

def compile(doc, tricks):
    """return the doc modified according to a single given trick."""
    return TreatedDoc(treat=expanded_trick, tricks=chosen_trick, status=status)
