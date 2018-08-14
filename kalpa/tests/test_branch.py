import itertools
import operator

import pytest
from pyramid import location

from . base import (
    Admin,
    BaseBranch,
    BaseNode,
    ChildNode,
    ColoredBranch,
    ColoredNode,
    DiamondBranch,
    DiamondNode,
    Leaf,
    Object,
    Person,
    Root,
    Specialty,
    ALIASED_NODES)


def test_branch_resource_type(root):
    """Accessing a branch 'leaf' returns a node instance of class Leaf."""
    assert isinstance(root['leaf'], Leaf)


def test_branch_lineage(root):
    """Leaf is a child resource of Root according to Pyramid lineage."""
    assert location.inside(root['leaf'], root)


def test_keyerror_for_nonexisting_branch(root):
    """Requesting a nonexisting child branch results in a KeyError."""
    with pytest.raises(KeyError):
        root['nonexistant']


def test_branch_cache(root):
    """Looking up the same sub-resource twice gives the same instance."""
    assert root['leaf'] is root['leaf']


def test_branch_cache_separation():
    """Instances do not share a branch cache."""
    first_root = Root(None)
    other_root = Root(None)
    assert first_root['leaf'] is not other_root['leaf']


@pytest.mark.parametrize('node', ['by_class', 'by_function', 'by_name'])
def test_branch_sources(root, node):
    """Defining a branch's node class can be done through multiple means."""
    assert isinstance(root[node], ChildNode)


@pytest.mark.parametrize('alias', ALIASED_NODES)
def test_branch_alias(root, alias):
    """Accessing the branch using aliased names returns the same type."""
    assert isinstance(root[alias], Leaf)


@pytest.mark.parametrize('alias', ALIASED_NODES)
def test_branch_alias_caching(root, alias):
    """Aliased resources are cached similarly to primary resources."""
    assert root[alias] is root[alias]


@pytest.mark.parametrize('pair', itertools.combinations(ALIASED_NODES, 2))
def test_branch_aliases_are_separate_instances(root, pair):
    """Aliased resources are their own separate instances."""
    first, second = pair
    assert root[first] is not root[second]


def test_branch_loading(root):
    """Child from objects 'collection' is of Object class."""
    assert isinstance(root['objects']['any'], Object)


def test_branch_loading_lineage(root):
    """Objects from collection is in lineage of Root and Collection."""
    leaf = root['objects']['any']
    assert location.inside(leaf, root)
    assert location.inside(leaf, root['objects'])


@pytest.mark.parametrize('user, node_class', [
    ('alice', Person), ('bob', Person), ('daniel', Admin), ('eve', Admin)])
def test_branch_alternate_loading(root, user, node_class):
    """People collection returns Person by default, Admin for some"""
    assert isinstance(root['people'][user], node_class)


@pytest.mark.parametrize('key_path', [
    ('objects', 'leaf'), ('people', 'charlie'), ('people', 'eve')])
def test_branch_load_cache(root, key_path):
    """Retrieving the same object twice should provide the same one."""
    first = reduce(operator.getitem, key_path, root)
    second = reduce(operator.getitem, key_path, root)
    assert first is second


def test_branch_load_nonexisting(root):
    """When __load__ returns a None value, this results in KeyError."""
    with pytest.raises(KeyError):
        root['people']['zenu']


def test_branch_load_missing_child_cls(root):
    """Accessing __load__ without a configured child class raises TypeError."""
    with pytest.raises(TypeError) as excinfo:
        root['bad_loader']['adam']

    # Check for the more informative message for the bad-config case
    msg_part = 'child resource class (__child_cls__) should be defined'
    assert msg_part in str(excinfo.value)


@pytest.mark.parametrize('key, node_class', [
    ('flute', Object), ('shoe', Object), ('escape', Specialty)])
def test_static_branch_on_loader(root, key, node_class):
    """Retrieving a static-attached branch from a node with a __child_cls__."""
    assert isinstance(root['objects'][key], node_class)


# ################################
# Tests for conditional branches
#
def test_conditional_always(root):
    """Branch with a fixed 'True' predicate is always present."""
    assert isinstance(root['conditional_always'], ChildNode)


def test_conditional_never(root):
    """Branch with a fixed 'False' predicate is always absent."""
    with pytest.raises(KeyError):
        root['condition_never']


def test_conditional_static_attr(root):
    """Branch with a predicate for a specific attribute value."""
    with pytest.raises(KeyError):
        root['conditional_request']
    root.request = 'conditional'
    assert isinstance(root['conditional_request'], ChildNode)


@pytest.mark.parametrize('user, access_granted, access_denied', [
    ('daniel', 'databases', 'servers'),
    ('eve', 'servers', 'databases')])
def test_conditional_loaded_attr(root, user, access_granted, access_denied):
    """Branch with predicate for a __load__'ed node attribute value.

    Tests declared conditional branches, verifies that failed predicates result
    in KeyError rather than lookups to __load__, which is verified by loading
    an undeclared path.
    """
    assert isinstance(root['people'][user][access_granted], Specialty)
    assert isinstance(root['people'][user]['undeclared'], ChildNode)
    with pytest.raises(KeyError):
        root['people'][user][access_denied]


# ##############################################
# Tests for subclassing and branch inheritance
#
@pytest.mark.parametrize('path, node_class', [
    ('base_branch', BaseBranch),
    ('colored_branch', BaseBranch),
    ('colored_branch', ColoredBranch),
    ('diamond_branch', BaseBranch),
    ('diamond_branch', ColoredBranch),
    ('diamond_branch', DiamondBranch)])
def test_inheritance(root, path, node_class):
    """Subclassed nodes are proper subclasses in the Python sense."""
    assert isinstance(root[path], node_class)


@pytest.mark.parametrize('branch', [
    'base_branch', 'colored_branch', 'diamond_branch'])
def test_inheritance_branch_shared(root, branch):
    """Base class and subclass share paths declared on base class."""
    assert isinstance(root[branch]['shared'], BaseNode)


def test_inheritance_branch_single_direction(root, path='sub_only'):
    """Branches on the subclass do not appear on the base class."""
    assert isinstance(root['colored_branch'][path], ColoredNode)
    assert isinstance(root['diamond_branch'][path], ColoredNode)
    with pytest.raises(KeyError):
        root['base_branch'][path]


@pytest.mark.parametrize('branch, node_class', [
    ('base_branch', BaseNode),
    ('colored_branch', ColoredNode),
    ('diamond_branch', DiamondNode)])
def test_inheritance_branch_override(root, branch, node_class):
    """Branches defined on the subclass take precedence over the baseclass.

    This precedence matches the MRO used for diamond inheritance.
    """
    assert isinstance(root[branch]['local'], node_class)
