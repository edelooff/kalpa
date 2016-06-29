#!/usr/bin/python

import pytest
from pyramid import location

import kalpa


@pytest.fixture
def basic_tree():
    """A simple root resource with a single static sub-resource.

    This implicitly tests the following components:

        - Static resource class attachment
        - Aliased resource attachment
    """
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
    """Returns a resource tree which is used for dynamic resource loading.

    This implicitly tests the following parts of kalpa:

        - Static resource class attachment
        - Child resource assignment to Branch classes
        - Child resource creation using the registered class
        - Child resource creation using a specified class
    """
    class Root(kalpa.Root):
        pass

    @Root.attach('objects')
    class Collection(kalpa.Branch):
        def __load__(self, path):
            return self._sprout(path, fruit='apple', twice=path * 2)

    @Root.attach('people')
    class People(kalpa.Branch):
        def __load__(self, path):
            return self._sprout_resource(Person, path, first=path[0].upper())

    @Collection.child_resource
    class Object(kalpa.Branch):
        pass

    @Object.attach('votes')
    class Votes(kalpa.Leaf):
        pass

    class Person(kalpa.Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'collection_cls': Collection,
        'object_cls': Object,
        'people_cls': People,
        'person_cls': Person}


@pytest.fixture
def mixed_tree():
    """Returns a resource tree which has mixed resource loading.

    This implicitly tests the following parts of kalpa:

        - Static resource class attachment
        - Child resource assignment to Branch classes
        - Child resource creation using the registered class
    """
    class Root(kalpa.Root):
        def __load__(self, path):
            return self._sprout(path)

    @Root.attach('spam')
    @Root.attach('eggs')
    class Static(kalpa.Leaf):
        pass

    @Root.child_resource
    class Dynamic(kalpa.Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'dynamic_cls': Dynamic,
        'static_cls': Static}


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
        """Child from 'collection' is of Object class (context selection)."""
        root = branching_tree['root']
        leaf = root['objects']['any']
        assert isinstance(leaf, branching_tree['object_cls'])

    def test_alternate_loaded_object_type(self, branching_tree):
        """Child from 'people' is of Person class (context selection)."""
        root = branching_tree['root']
        leaf = root['people']['alice']
        assert isinstance(leaf, branching_tree['person_cls'])

    def test_object_lineage(self, branching_tree):
        """Objects from collection is in lineage of Root and Collection."""
        root = branching_tree['root']
        leaf = root['objects']['any']
        assert location.inside(leaf, root)
        assert location.inside(leaf, root['objects'])

    def test_alternate_object_lineage(self, branching_tree):
        """Objects from collection is in lineage of Root and Collection."""
        root = branching_tree['root']
        leaf = root['people']['bob']
        assert location.inside(leaf, root)
        assert location.inside(leaf, root['people'])

    def test_object_caching(self, branching_tree):
        """Retrieving the same object twice should provide the same one."""
        root = branching_tree['root']
        assert root['objects']['leaf'] is root['objects']['leaf']

    def test_alternate_object_caching(self, branching_tree):
        """Retrieving the same object twice should provide the same one."""
        root = branching_tree['root']
        assert root['people']['eve'] is root['people']['eve']


class TestMixedResource(object):
    def test_static_resource_load(self, mixed_tree):
        """Retrieves a statically attached resource from the tree."""
        root = mixed_tree['root']
        assert isinstance(root['spam'], mixed_tree['static_cls'])
        assert isinstance(root['eggs'], mixed_tree['static_cls'])

    def test_dynamic_resource_load(self, mixed_tree):
        """Retrieves a resource from the tree through __load__."""
        root = mixed_tree['root']
        assert isinstance(root['ham'], mixed_tree['dynamic_cls'])
        assert isinstance(root['bacon'], mixed_tree['dynamic_cls'])


class TestAttributeAccess(object):
    def test_simple_attribute_access(self, branching_tree):
        """Keywords given for object creation are available as attributes."""
        root = branching_tree['root']
        pie = root['objects']['pie']
        assert pie.fruit == 'apple'
        assert pie.twice == 'piepie'

    def test_delegated_attribute_access(self, branching_tree):
        """Attributes access searches up along lineage for requested attr."""
        root = branching_tree['root']
        person = root['objects']['bob']
        votes = person['votes']
        assert votes.fruit == person.fruit
        assert votes.fruit == 'apple'

    def test_attribute_cached_access(self, branching_tree):
        """Accessing parented attribute places it on local object."""
        root = branching_tree['root']
        votes = root['objects'][21]['votes']
        assert 'twice' not in vars(votes)
        assert votes.twice == 42
        assert 'twice' in vars(votes)

    def test_only_delegate_initial_attributes(self, branching_tree):
        """Only attributes provided during resource created are delegated."""
        root = branching_tree['root']
        leaf = root['objects']['leaf']
        leaf.name = 'example'
        with pytest.raises(AttributeError):
            leaf['votes'].name

    def test_only_delegate_initial_attribute_values(self, branching_tree):
        """Only the initial values of attributes are delegated."""
        root = branching_tree['root']
        leaf = root['objects']['leaf']
        leaf.fruit = 'pear'
        assert leaf['votes'].fruit == 'apple'

    def test_attributes_for_custom_children(self, branching_tree):
        """Children created by manual resource selection have same attrs."""
        root = branching_tree['root']
        assert root['people']['emily'].first == 'E'
        assert root['people']['peter'].first == 'P'
