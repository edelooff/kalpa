#!/usr/bin/python

import pytest
from pyramid import location

import kalpa


@pytest.fixture
def basic_tree():
    """A simple root resource with a single static sub-resource."""
    class Root(kalpa.Root):
        pass

    @Root.attach('leaf', aliases=['foliage', 'leaves'])
    class Leaf(kalpa.Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'leaf_cls': Leaf}


@pytest.fixture
def branching_tree():
    class Root(kalpa.Root):
        pass

    @Root.attach('objects')
    class Collection(kalpa.Branch):
        def __getitem__(self, path):
            return self._sprout(path, fruit='apple', twice=path * 2)

    @Collection.child_resource
    class Object(kalpa.Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'collection_cls': Collection,
        'object_cls': Object}


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


class TestBranchAliasing(object):
    def test_alias_access(self, basic_tree):
        """Accessing the sub-resource using aliased names gives resource."""
        root = basic_tree['root']
        assert isinstance(root['foliage'], basic_tree['leaf_cls'])
        assert isinstance(root['leaves'], basic_tree['leaf_cls'])

    def test_alias_resouce_caching(self, basic_tree):
        """Aliased resources are cached similarly to primary resources."""
        root = basic_tree['root']
        alias_one = root['foliage']
        alias_two = root['leaves']
        assert alias_one is root['foliage']
        assert alias_two is root['leaves']

    def test_alias_are_separate_instances(self, basic_tree):
        """Aliased resources are their own separate instances."""
        root = basic_tree['root']
        primary = root['leaf']
        alias_one = root['foliage']
        alias_two = root['leaves']
        assert primary is not alias_one
        assert primary is not alias_two
        assert alias_one is not alias_two


class TestBranchingResource(object):
    def test_loaded_object_type(self, branching_tree):
        """Object from collection is of Object class, for context selection."""
        root = branching_tree['root']
        leaf = root['objects']['any']
        assert isinstance(leaf, branching_tree['object_cls'])

    def test_object_lineage(self, branching_tree):
        """Objects from collection is in lineage of Root and Collection."""
        root = branching_tree['root']
        leaf = root['objects']['any']
        assert location.inside(leaf, root)
        assert location.inside(leaf, root['objects'])

    def test_object_caching(self, branching_tree):
        """Retrieving the same object twice should provide the same one."""
        root = branching_tree['root']
        assert root['objects']['leaf'] is root['objects']['leaf']
