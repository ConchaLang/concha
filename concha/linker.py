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
__version__ = '1.0'
__all__ = [
    'link'
]

__author__ = 'Pascual de Juan <pascual.dejuan@gmail.com>'

from random import choice
from collections import namedtuple
from trick import expand_trick, match_tricks

TreatedDoc = namedtuple('TreatedDoc', ['treat', 'tricks', 'status'])


def link(doc, tricks):
    """return the doc modified according to given tricks."""
    candidate_tricks = match_tricks(doc, tricks)
    expanded_trick, chosen_trick = (None,)*2
    if len(candidate_tricks) > 0:
        chosen_trick = choice(candidate_tricks)
        expanded_trick = expand_trick(chosen_trick, doc)
        status = 201
    else:
        expanded_trick = 'No trick'  # TODO not in English
        status = 404
    return TreatedDoc(treat=expanded_trick, tricks=chosen_trick, status=status)
