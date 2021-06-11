# Copyright 2021 Open Source Robotics Foundation, Inc.
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

import importlib.resources
import pathlib
from typing import List

from lxml import etree

import nodl
from nodl.types import Node

from sros2.policy import (
    dump_policy,
    load_policy,
    POLICY_VERSION,
)


_POLICY_FILE_EXTENSION = '.policy.xml'

def get_policy(policy_file_path: pathlib.Path) -> etree._ElementTree:
    # Reference: https://github.com/ros2/sros2/blob/e5e90f05c3d800c51648e02d48d30ed4d6158820/sros2/sros2/verb/generate_policy.py#L60-L68
    if policy_file_path.is_file():
        return load_policy(policy_file_path)
    else:
        enclaves = etree.Element('enclaves')
        policy = etree.Element('policy')
        policy.attrib['version'] = POLICY_VERSION
        policy.append(enclaves)
        return policy

def convert_to_policy(policy_file_path: pathlib.Path, nodl_description: List[Node]) -> etree._ElementTree:
    policy = get_policy(policy_file_path)

    for node in nodl_description:
        # profile: need to find node path somehow

        # Below info can be extracted from `nodl.Node` class
        # subscriptions
        # publishers
        # replies - server/action
        # requests - server/action
        # parameters

        # On this note, there is no mention of actions in
        # `sros2/generate_policy.py` (https://github.com/ros2/sros2/blob/e5e90f05c3d800c51648e02d48d30ed4d6158820/sros2/sros2/verb/generate_policy.py#L124-L141)
        # is this something to be looked at?
        pass

    return policy


def write_policy(policy_file_path: pathlib.Path, policy: etree._ElementTree) -> None:
    with open(policy_file_path, 'w') as stream:
        dump_policy(policy, stream)
