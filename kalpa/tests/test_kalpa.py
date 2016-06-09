#!/usr/bin/python

import pytest
from pyramid import location

import kalpa


@pytest.fixture
def basic_root():
    """A simple root resource with a single static sub-resource."""
    class Root(kalpa.Root):
        pass

    @Root.attach('leaf')
    class Leaf(kalpa.Leaf):
        pass

    return Root(None)


class TestBasicResource(object):
    def test_sub_resource_lineage(self, basic_root):
        """Leaf is a child resource of Root according to Pyramid lineage."""
        leaf = basic_root['leaf']
        assert location.inside(leaf, basic_root)

    def test_keyerror_for_nonexistant_sub_resource(self, basic_root):
        with pytest.raises(KeyError):
            basic_root['nonexistant']

    def test_contains_false_before_access(self, basic_root):
        """Before accessing the leaf, the root has no child by that name."""
        assert 'leaf' not in basic_root

    def test_contains_true_after_access(self, basic_root):
        """After accessing the leaf, the root has a child by that name."""
        basic_root['leaf']
        assert 'leaf' in basic_root

    def test_multiple_lookups_same_resource(self, basic_root):
        """Looking up the same sub-resource twice gives the same instance."""
        first = basic_root['leaf']
        second = basic_root['leaf']
        assert first is second
