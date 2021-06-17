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

import sys
import argparse
import pathlib
from argcomplete.completers import FilesCompleter

import nodl
from nodl._index import _FILE_EXTENSION as _NODL_FILE_EXTENSION
from ros2cli.verb import VerbExtension

from nodl_to_policy.policy import (
    convert_to_policy,
    write_policy,
    _POLICY_FILE_EXTENSION
)


class _ConvertVerb(VerbExtension):
    """Convert NoDL XML documents to ROS 2 Access Control Policies"""

    def add_arguments(self, parser: argparse.ArgumentParser, cli_name: None = None) -> None:
        """Argument addition for the `convert` verb."""

        arg = parser.add_argument(
            'NODL_FILE_PATHS',
            nargs='*',
            default=[],
            metavar='nodl_file',
            type=pathlib.Path,
            help=f'Specific {_NODL_FILE_EXTENSION} file(s) to convert.'
        )
        arg.completer = FilesCompleter(allowednames=[_NODL_FILE_EXTENSION], directories=False)

        parser.add_argument(
            'POLICY_FILE_PATH',
            metavar='policy_file',
            type=pathlib.Path,
            help='Path of the policy XML file'
        ).completer = FilesCompleter(allowednames=[_POLICY_FILE_EXTENSION], directories=False)

        parser.add_argument('-p', '--print', action='store_true', help='Print converted output.')

    def main(self, *, args: argparse.Namespace) -> int:
        """High level logic employed by the `convert` verb."""

        if not args.NODL_FILE_PATHS:
            print('No files to validate', file=sys.stderr)
            return 1

        for nodl_file_path in args.NODL_FILE_PATHS:
            if not nodl_file_path.is_file():
                print(f'{nodl_file_path} is not a file')
                return 1

            try:
                nodl_description = nodl.parse(path=nodl_file_path)
            except nodl.errors.NoDLError as e:
                print(f'Failed to parse {nodl_file_path}', file=sys.stderr)
                print(e, file=sys.stderr)
                return 1

            policy = convert_to_policy(args.POLICY_FILE_PATH, nodl_description)
            write_policy(args.POLICY_FILE_PATH, policy, args.print)

        return 0
