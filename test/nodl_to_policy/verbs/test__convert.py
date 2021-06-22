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

import argparse

import pytest
from nodl_to_policy._verb import _convert
import nodl


@pytest.fixture
def verb() -> _convert._ConvertVerb:
    return _convert._ConvertVerb()


@pytest.fixture
def parser(verb):
    parser = argparse.ArgumentParser()
    verb.add_arguments(parser)
    return parser


def test_accepts_valid_nodl_path(mocker, parser, test_nodl, verb):
    mocker.patch('nodl_to_policy._verb._convert.nodl.parse')

    args = parser.parse_args(['-i', str(test_nodl)])
    assert not verb.main(args=args)


def test_accepts_valid_policy_path(mocker, parser, test_nodl, test_policy, verb):
    mocker.patch('nodl_to_policy._verb._convert.nodl.parse')

    args = parser.parse_args(['-i', str(test_nodl), '-o', str(test_policy)])
    assert not verb.main(args=args)


def test_fails_no_nodl_file(mocker, parser, tmp_path, verb):
    mocker.patch('nodl_to_policy._verb._convert.pathlib.Path.cwd', return_value=tmp_path)

    args = parser.parse_args(['-i', ''])
    assert verb.main(args=args)


def test_fails_sneaky_dir(mocker, parser, tmp_path, verb):
    sneakydir = tmp_path / 'test.nodl.xml'
    sneakydir.mkdir()

    args = parser.parse_args(['-i', str(tmp_path.resolve())])
    assert verb.main(args=args)


def test_accepts_valid_nodl(mocker, parser, test_nodl, verb):
    args = parser.parse_args(['-i', str(test_nodl)])

    assert not verb.main(args=args)


def test_accepts_valid_policy(mocker, parser, test_nodl, test_policy, verb):
    args = parser.parse_args(['-i', str(test_nodl), '-o', str(test_policy)])

    assert not verb.main(args=args)


def test_fails_invalid_nodl(mocker, parser, test_nodl_invalid, verb):
    # Check that the NoDL parser throws with an invalid NoDL file
    mocker.patch(
        'nodl_to_policy._verb._convert.nodl.parse',
        side_effect=nodl.errors.InvalidNoDLError(mocker.MagicMock()),
    )
    args = parser.parse_args(['-i', str(test_nodl_invalid)])

    assert verb.main(args=args)


# def test_fails_invalid_policy(mocker, parser, test_nodl, test_policy_invalid, verb):
#    # Check that the NoDL parser throws with an invalid NoDL file
#    mocker.patch(
#        'nodl_to_policy._verb._convert.convert_to_policy',
#        side_effect=RuntimeError(mocker.MagicMock()),
#    )
#    args = parser.parse_args(['-i', str(test_nodl), '-o', str(test_policy_invalid)])
#
#    assert verb.main(args=args)


def test_prints_to_console(mocker, parser, test_nodl, test_policy, verb):
    print_mock = mocker.patch('nodl_to_policy._verb._convert.write_policy', autospec=True)

    args = parser.parse_args(['-o', str(test_policy), '-i', str(test_nodl), '-p'])

    assert not verb.main(args=args)
    assert print_mock.call_args.args[-1]  # `print` argument is True
