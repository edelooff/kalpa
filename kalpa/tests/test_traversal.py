"""Tests compatiblity and integration with Pyramid's traversal utlities."""

import operator

import pytest
from pyramid import traversal


def test_find_root(root):
    """For a given resource, Pyramid can find its root."""
    assert traversal.find_root(root) == root
    assert traversal.find_root(root['people']['alice']) == root
    assert traversal.find_root(root['objects']['egg']['votes']) == root


@pytest.mark.parametrize('path, keys', [
    ('/', ()),
    ('/people/alice', ('people', 'alice')),
    ('/objects/apple/votes', ('objects', 'apple', 'votes'))])
def test_find_resource(root, path, keys):
    """Resolving paths yields the expected resource."""
    resource = reduce(operator.getitem, keys, root)
    assert traversal.find_resource(root, path) == resource


@pytest.mark.parametrize('keys, path', [
    (('people', 'bob'), '/people/bob'),
    (('objects', 'pear', 'votes'), '/objects/pear/votes')])
def test_resource_path(root, keys, path):
    """Resources generate the expected path."""
    resource = reduce(operator.getitem, keys, root)
    assert traversal.resource_path(resource) == path


@pytest.mark.parametrize('alias', ['leaf', 'leaves', 'foliage'])
def test_resource_path_aliased(root, alias):
    """Finds a resource by its aliases and verifies the canonical path."""
    resource = traversal.find_resource(root, [alias])
    assert traversal.resource_path(resource) == '/leaf'
