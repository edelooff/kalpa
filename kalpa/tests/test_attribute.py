import pytest

from . base import (
    ADMINS,
    PEOPLE)


def test_root_request(root):
    """The traversal root captures the 'request' correctly."""
    assert root.request == 'mock_request'


def test_delegated_attribute_access(root):
    """Attributes access is delegated up along lineage."""
    assert root.request is root['leaf'].request


def test_delegated_attribute_cache(root):
    """Accessing delegated attributes place them on the local instance."""
    assert 'request' not in vars(root['leaf'])
    assert root['leaf'].request
    assert 'request' in vars(root['leaf'])


def test_delegate_only_initial_attributes(root):
    """Only attributes provided during resource creation are delegated."""
    root.new_attr = 'example'
    with pytest.raises(AttributeError):
        root['leaf'].new_attr


def test_delegate_lazy_value_determination(root):
    """Delegated attributes provide value at request time, but don't update."""
    root.request = 'updated_request'
    assert root['leaf'].request == 'updated_request'
    root.request = 'original_request'
    assert root['leaf'].request == 'updated_request'


@pytest.mark.parametrize('name, attributes', PEOPLE.items())
def test_branch_load_attributes(root, name, attributes):
    """Dict returned from __load__ is used to create attributes."""
    person = root['people'][name]
    for attr, value in attributes.items():
        assert getattr(person, attr) == value


@pytest.mark.parametrize('name, attributes', ADMINS.items())
def test_branch_child_attributes(root, name, attributes):
    """Keywords for _child are used to create attributes from."""
    person = root['people'][name]
    for attr, value in attributes.items():
        assert getattr(person, attr) == value


@pytest.mark.parametrize('name', ['egg', 'telephone'])
def test_branch_delegated_access(root, name):
    """Attribute access delegation for dynamically created resources."""
    assert root['objects'][name].len == len(name)  # direct access
    assert root['objects'][name]['votes'].len == len(name)  # delegated access


@pytest.mark.parametrize('name', ['egg', 'telephone'])
def test_branch_delegated_cache(root, name):
    """Delegated access cache for dynamically created resources."""
    node = root['objects'][name]
    assert 'twice' not in vars(node['votes'])
    assert node['votes'].twice == name * 2
    assert 'twice' in vars(node['votes'])


@pytest.mark.parametrize('name', ['egg', 'telephone'])
def test_branch_delegate_only_initial(root, name):
    """For dynamically created resource, only initial values are delegated."""
    node = root['objects'][name]
    node.new_attr = 'example'
    with pytest.raises(AttributeError):
        node['votes'].new_attr
