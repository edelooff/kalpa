import operator

import pytest
from kalpa.util import (
    lineage,
    parent_by_class,
    parent_by_name)
from pyramid import location

from . base import (
    Root,
    People,
    Person)


def test_util_lineage(root):
    """Assures that kalpa's lineage function works similarly to Pyramid's."""
    resource = root['path']['eggs']['bacon']['spam']['spam']
    assert list(location.lineage(resource)) == list(lineage(resource))


@pytest.mark.parametrize('selector, expected_key_path', [
    (Person, ('people', 'alice')),
    (People, ('people',)),
    (Root, ())])
def test_find_parent_by_class(root, selector, expected_key_path):
    """Finding a parent resource by its class."""
    alice = root['people']['alice']
    expected = reduce(operator.getitem, expected_key_path, root)
    assert parent_by_class(alice, selector) is expected


@pytest.mark.parametrize('selector, expected_key_path', [
    ('Person', ('people', 'alice')),
    ('People', ('people',)),
    ('Root', ())])
def test_find_parent_by_class_name(root, selector, expected_key_path):
    """Finding a parent resource by its class name."""
    alice = root['people']['alice']
    expected = reduce(operator.getitem, expected_key_path, root)
    assert parent_by_class(alice, selector) is expected


@pytest.mark.parametrize('selector', [object, 'Nonexisting'])
def test_find_parent_by_class_no_match(root, selector):
    """If no parent matches the given class, finder raises LookupError."""
    with pytest.raises(LookupError):
        parent_by_class(root, selector)


def test_find_parent_by_name(root):
    """Finding a parent resource by its resource name."""
    apple_votes = root['objects']['apple']['votes']
    assert parent_by_name(apple_votes, 'votes') is apple_votes
    assert parent_by_name(apple_votes, 'apple') is root['objects']['apple']
    assert parent_by_name(apple_votes, 'objects') is root['objects']
    assert parent_by_name(apple_votes, None) is root


def test_find_parent_by_name_no_match(root):
    """If no parent matches the given name, finder raises LookupError."""
    with pytest.raises(LookupError):
        parent_by_name(root, 'olive')
