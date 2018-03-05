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
from syntax_tree import SyntaxTree

Artifact = namedtuple('Artifact', ['tree', 'used_tricks', 'status'])


def resolve_artifact(artifacts):
    """Decide the most appropriate among the possible artifacts."""
    choices = []
    max_complexity = max([len(x.used_tricks) for x in artifacts])
    for artifact in artifacts:
        if len(artifact.used_tricks) == max_complexity:
            if not choices:
                choices.append(artifact)
            elif artifact.status < choices[0].status:
                choices.clear()
                choices.append(artifact)
            elif artifact.status == choices[0].status:
                choices.append(artifact)
    return choice(choices)


def linker(tree, tricks):
    """Return an Artifact according to a given source tree and trick domain."""
    artifacts = []
    candidate_tricks = match_tricks(tree, tricks)
    if len(candidate_tricks) > 0:
        for trick_idx in candidate_tricks:
            artifact = compiler(tree, trick_idx, tricks)
            artifacts.append(artifact)
            new_candidate_tricks = match_tricks(artifact.tree, tricks)
            original = set(candidate_tricks)
            new = set(new_candidate_tricks)
            candidate_tricks.extend(set(new.difference(original)))  # add difference to candidates
    elif len(error_domain) > 0:
        for trick in error_domain:
            artifacts.append(compiler(tree, trick, error_domain))
    else:  # Fallback in English
        artifacts.append(Artifact(tree={'root': {'form': 'NoTrick'}}, used_tricks=[], status='600'))  # Not a HTTP code
    return resolve_artifact(artifacts)


def compiler(tree, trick_idx, tricks):
    """Return a new Artifact generated according to a single given trick."""
    r_tree = None
    r_status = None
    trick = tricks[trick_idx]
    context = {'d': tree}
    if 'when' in trick:
        method = trick['when']['method']
        if method == 'POST':
            uri = trick['when']['uri'].format_map(context)
            response = requests.post(url=uri, json=trick['when']['body'])
            r_status = str(response.status_code)
            if 'json' in response.headers['content-type']:
                context.update({'r': {'body': json.loads(response.text)}})
            else:
                context.update({'r': {'body': ''}})
        elif method == 'PUT':
            uri = trick['when']['uri'].format_map(context)
            response = requests.put(url=uri, json=trick['when']['body'])
            r_status = str(response.status_code)
            if 'json' in response.headers['content-type']:
                context.update({'r': {'body': json.loads(response.text)}})
            else:
                context.update({'r': {'body': ''}})
        elif method == 'GET':
            uri = trick['when']['uri'].format_map(context)
            response = requests.get(url=uri)
            r_status = str(response.status_code)
            if 'json' in response.headers['content-type']:
                context.update({'r': {'body': json.loads(response.text)}})
            else:
                context.update({'r': {'body': ''}})
        elif method == 'DELETE':
            uri = trick['when']['uri'].format_map(context)  # TODO protect
            response = requests.delete(url=uri)
            r_status = str(response.status_code)
            if 'json' in response.headers['content-type']:
                context.update({'r': {'body': json.loads(response.text)}})
            else:
                context.update({'r': {'body': ''}})
        elif method == 'TREAT':
            pointed_content = SyntaxTree.point_to_content(context, trick['when']['uri'])
            sub_tree = SyntaxTree.new_from_tree(context, trick['when']['uri'])
            sub_artifact = linker(sub_tree, tricks)  # First pass, only the to_tree.
            r_status = sub_artifact.status
            if r_status in trick['then']:
                context.update({'r': sub_artifact.tree})
                replacement_text = trick['then'][r_status].format_map(context)
                treated_source = SyntaxTree.new_from_text(tree.to_string_replacing(pointed_content, replacement_text))
                treated_artifact = linker(treated_source, tricks)  # Second pass, to_tree response expanded in from_tree
                return Artifact(
                    tree=treated_artifact.tree,
                    used_tricks=[trick_idx] + sub_artifact.used_tricks + treated_artifact.used_tricks,
                    status=treated_artifact.status
                )
            else:  # reply error in to_tree with a not implemented r_status
                return Artifact(
                    tree=sub_tree,
                    used_tricks=[trick_idx] + sub_artifact.used_tricks,
                    status='501'
                )
        else:
            r_status = '501'  # Unknown method
    else:  # No 'when' in trick means "do the 'then' part"
        r_status = '200'
    if r_status in trick['then']:
        then = trick['then'][r_status]
        r_tree = SyntaxTree.new_from_text(then.format_map(context))
    else:
        r_status = '501'
    return Artifact(tree=r_tree, used_tricks=[trick_idx], status=r_status)
