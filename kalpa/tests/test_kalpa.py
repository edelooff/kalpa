#!/usr/bin/python

import pytest
from pyramid import location

import kalpa


@pytest.fixture
def basic_tree():
    """A simple root resource with a single static sub-resource."""
    class Root(kalpa.Root):
        pass

    @Root.attach('leaf')
    class Leaf(kalpa.Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'leaf_cls': Leaf}


class TestBasicResource(object):
    def test_sub_resource_type(self, basic_tree):
        """Leaf is an instance of the Leaf class, for context selection."""
        root = basic_tree['root']
        leaf = root['leaf']
        assert isinstance(leaf, basic_tree['leaf_cls'])

    def test_sub_resource_lineage(self, basic_tree):
        """Leaf is a child resource of Root according to Pyramid lineage."""
        root = basic_tree['root']
        leaf = root['leaf']
        assert location.inside(leaf, root)

    def test_keyerror_for_nonexistant_sub_resource(self, basic_tree):
        root = basic_tree['root']
        with pytest.raises(KeyError):
            root['nonexistant']

    def test_contains_false_before_access(self, basic_tree):
        """Before accessing the leaf, the root has no child by that name."""
        root = basic_tree['root']
        assert 'leaf' not in root

    def test_contains_true_after_access(self, basic_tree):
        """After accessing the leaf, the root has a child by that name."""
        root = basic_tree['root']
        root['leaf']
        assert 'leaf' in root

    def test_multiple_lookups_same_resource(self, basic_tree):
        """Looking up the same sub-resource twice gives the same instance."""
        root = basic_tree['root']
        first = root['leaf']
        second = root['leaf']
        assert first is second
