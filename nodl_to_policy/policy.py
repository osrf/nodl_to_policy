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

import pathlib
import sys
from typing import Dict, List, Tuple

from lxml import etree

import nodl  # noqa: F401
from nodl.types import (
    Node,
    PubSubRole,
    ServerClientRole,
)

from sros2.policy import (
    POLICY_VERSION,
    dump_policy,
    load_policy,
)


_POLICY_FILE_EXTENSION = '.policy.xml'


def get_policy(policy_file_path: pathlib.Path) -> etree._ElementTree:
    """Load (or creates) a policy element in an LXML ElementTree."""
    if policy_file_path.is_file():
        return load_policy(policy_file_path)
    else:
        enclaves = etree.Element('enclaves')
        policy = etree.Element('policy')
        policy.attrib['version'] = POLICY_VERSION
        policy.append(enclaves)
        return policy


def get_profile(policy: etree._ElementTree, node_name: str) -> etree._ElementTree:
    """Return a node's respective profile tag in an LXML ElementTree."""
    enclave = policy.find(path=f'enclaves/enclave[@path=""]')
    if enclave is None:
        enclave = etree.Element('enclave')
        # unqualified enclave path for now, refer to security enclaves design article
        # TODO: Verify that this is how enclave paths should work
        enclave.attrib['path'] = ''
        profiles = etree.Element('profiles')
        enclave.append(profiles)
        enclaves = policy.find('enclaves')
        enclaves.append(enclave)

    profile = enclave.find(path=f'profiles/profile[@ns=""][@node="{node_name}"]')
    if profile is None:
        profile = etree.Element('profile')
        # namespace information not provided in NoDL description yet
        # TODO: Verify that this is how node namespaces should work
        profile.attrib['ns'] = ''
        profile.attrib['node'] = node_name
        profiles = enclave.find('profiles')
        profiles.append(profile)

    return profile


def get_permission(
    profile: etree._ElementTree, permission_type: str, rule_type: str,
    rule_expression: str
) -> etree._ElementTree:
    """Return (or create) an appropriate permission (actions/services/topics) tag."""
    permissions = profile.find(path=f'{permission_type}s[@{rule_type}="{rule_expression}"]')
    if permissions is None:
        permissions = etree.Element(permission_type + 's')
        permissions.attrib[rule_type] = rule_expression
        profile.append(permissions)
    return permissions


def add_permission(
    profile: etree._ElementTree, node: Node, permission_type: str, rule_type: str,
    rule_expression: str, expressions: Dict
) -> None:
    """For each service/action/topic, the actual expression tag is added to the ElementTree."""
    # get permission
    permissions = get_permission(profile, permission_type, rule_type, rule_expression)

    # add permission
    for expression_name in expressions:
        permission = etree.Element(permission_type)
        if expression_name.startswith(node.name + '/'):
            permission.text = '~' + expression_name[len(node.name):]
        elif expression_name.startswith('/'):
            permission.text = expression_name[len('/'):]
        else:
            permission.text = expression_name
        permissions.append(permission)


def convert_to_policy(
    policy_file_path: pathlib.Path, nodl_description: List[Node]
) -> etree._ElementTree:
    """Handle the main logic for conversion from NoDL description to access control policy."""
    policy = get_policy(policy_file_path)

    for node in nodl_description:
        # Profile: need to find enclave path and node namespace somehow
        profile = get_profile(policy, node.name)

        # TODO: Parameters? Not specified in access control policy
        subscribe_topics, publish_topics = _get_topics_by_role(node.topics)
        reply_services, request_services = _get_services_by_role(node.services)
        reply_actions, request_actions = _get_actions_by_role(node.actions)

        # Permissions are not added if any of the expression collections are empty
        # TODO: Refactor `_get_[]_by_role` to return Optional[Dict]
        # This helps make the proceeding logic look simpler
        if len(subscribe_topics) != 0:
            add_permission(profile, node, 'topic', 'subscribe', 'ALLOW', subscribe_topics)
        if len(publish_topics) != 0:
            add_permission(profile, node, 'topic', 'publish', 'ALLOW', publish_topics)
        if len(reply_services) != 0:
            add_permission(profile, node, 'service', 'reply', 'ALLOW', reply_services)
        if len(request_services) != 0:
            add_permission(profile, node, 'service', 'request', 'ALLOW', request_services)
        if len(reply_actions) != 0:
            add_permission(profile, node, 'action', 'execute', 'ALLOW', reply_actions)
        if len(request_actions) != 0:
            add_permission(profile, node, 'action', 'call', 'ALLOW', request_actions)

    return policy


def write_policy(
    policy_file_path: pathlib.Path, policy: etree._ElementTree, print_policy
) -> None:
    """Write a generated policy ElementTree to an XML file, and optionally to the console."""
    with open(policy_file_path, 'w') as stream:
        dump_policy(policy, stream)
    if print_policy:
        dump_policy(policy, sys.stdout)


def _get_topics_by_role(topics: Dict) -> Tuple[Dict, Dict]:
    subscribe_topics = {}
    publish_topics = {}
    for _, topic in topics.items():
        if PubSubRole(topic.role) is PubSubRole.SUBSCRIPTION:
            subscribe_topics[topic.name] = topic
        elif PubSubRole(topic.role) is PubSubRole.PUBLISHER:
            publish_topics[topic.name] = topic
        else:  # PubSubRole(topic.role) is PubSubRole.BOTH
            subscribe_topics[topic.name] = topic
            publish_topics[topic.name] = topic
    return subscribe_topics, publish_topics


def _get_services_by_role(services: Dict) -> Tuple[Dict, Dict]:
    reply_services = {}
    request_services = {}
    for _, service in services.items():
        if ServerClientRole(service.role) is ServerClientRole.CLIENT:
            request_services[service.name] = service
        elif ServerClientRole(service.role) is ServerClientRole.SERVER:
            reply_services[service.name] = service
        else:  # ServerClientRole(service.role) is ServerClientRole.BOTH
            request_services[service.name] = service
            reply_services[service.name] = service

    return reply_services, request_services


def _get_actions_by_role(actions: Dict) -> Tuple[Dict, Dict]:
    return _get_services_by_role(actions)  # `nodl.types.Action` also share ServerClientRole enums
