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
    'linker', 'compiler', 'Artifact'
]

import json
import requests
from random import choice
from collections import namedtuple
from trick import match_tricks, error_domain
from connl_tree import sub_tree, text_parse, ConnlTree

Artifact = namedtuple('Artifact', ['doc', 'used_tricks', 'status'])


def linker(source, tricks):
    """Return an Artifact according to a given source doc and trick domain."""
    artifacts = []
    candidate_tricks = match_tricks(source, tricks)
    if len(candidate_tricks) > 0:
        for trick_idx in candidate_tricks:
            artifact = compiler(source, trick_idx, tricks)
            artifacts.append(artifact)
            new_candidate_tricks = match_tricks(artifact.doc, tricks)
            original = set(candidate_tricks)
            new = set(new_candidate_tricks)
            candidate_tricks.extend(set(new.difference(original)))  # add difference to candidates
    elif len(error_domain) > 0:
        for trick in error_domain:
            artifacts.append(compiler(source, trick, error_domain))
    else:  # Fallback in English
        artifacts.append(Artifact(doc={'ROOT': {'FORM': 'NoTrick'}}, used_tricks=[], status='404'))
    chosen_artifact = choice(artifacts)  # TODO find out a better criteria *****************
    return chosen_artifact


def compiler(source, trick_idx, tricks):
    """Return a new Artifact generated according to a single given trick."""
    r_doc = None
    r_status = None
    trick = tricks[trick_idx]
    context = {'d': source}
    if 'when' in trick:
        method = trick['when']['method']
        if method == 'POST':
            uri = trick['when']['uri'].format_map(context)
            response = requests.post(url=uri, json=trick['when']['body'])
            r_status = str(response.status_code)
            context.update({'r': {'body': json.loads(response.text)}})
        elif method == 'GET':
            uri = trick['when']['uri'].format_map(context)
            response = requests.get(url=uri)
            r_status = str(response.status_code)
            context.update({'r': {'body': json.loads(response.text)}})
        elif method == 'TREAT':
            source_branch = sub_tree(context, trick['when']['uri'])
            sub_target = '{{{}}}'.format(source_branch.key)
            sub_doc = text_parse(sub_target.format_map(source_branch.parent))
            sub_artifact = linker(sub_doc, tricks)
            r_status = sub_artifact.status
            if r_status in trick['then']:
                context.update({'r': sub_artifact.doc})
                replacement_branch = sub_tree(context, trick['then'][r_status])
                replacement_branch.tree.renumber(source_branch.tree.min() - 1)
                threshold = source_branch.tree.max() + 1
                delta = replacement_branch.tree.len() - source_branch.tree.len()
                treated_source = source.deep_replacement(
                    source_branch.parent, source_branch.key,
                    replacement_branch.tree, delta, threshold
                )
                treated_artifact = linker(treated_source, tricks)
                return Artifact(
                    doc=treated_artifact.doc,
                    used_tricks=[trick_idx] + treated_artifact.used_tricks,
                    status=treated_artifact.status
                )
            else:  # reply error in sub_doc with a not found r_status
                return Artifact(
                    doc=sub_doc,
                    used_tricks=[trick_idx] + sub_artifact.used_tricks,
                    status='404'
                )
        else:
            r_status = '400'  # TODO do other methods
    else:  # No 'when' in trick means "do the 'then' part"
        r_status = '200'
    if r_status in trick['then']:
        then = trick['then'][r_status]
        r_doc = text_parse(then.format_map(context))
    else:
        r_status = '400'
    return Artifact(doc=r_doc, used_tricks=[trick_idx], status=r_status)
