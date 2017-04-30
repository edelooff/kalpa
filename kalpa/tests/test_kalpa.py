import pytest


@pytest.fixture
def basic_tree():
    """A simple root resource with a single static sub-resource.

    This implicitly tests the following components:

        - Static resource class attachment
        - Aliased resource attachment
    """
    from kalpa import Root, Leaf

    class Root(Root):
        pass

    @Root.attach('leaf', aliases=['foliage', 'leaves'])
    class Leaf(Leaf):
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
    from kalpa import Root, Branch, Leaf

    class Root(Root):
        pass

    @Root.attach('objects')
    class Collection(Branch):
        def __load__(self, path):
            return self._child(path, fruit='apple', twice=path * 2)

    @Root.attach('people')
    class People(Branch):
        def __load__(self, path):
            return self._child(Person, path, first=path[0].upper())

    @Collection.child_resource
    class Object(Branch):
        pass

    @Object.attach('votes')
    class Votes(Leaf):
        pass

    class Person(Leaf):
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
    from kalpa import Root, Leaf

    class Root(Root):
        def __load__(self, path):
            return self._child(path)

    @Root.attach('spam')
    @Root.attach('eggs')
    class Static(Leaf):
        pass

    @Root.child_resource
    class Dynamic(Leaf):
        pass

    return {
        'root': Root(None),
        'root_cls': Root,
        'dynamic_cls': Dynamic,
        'static_cls': Static}


@pytest.fixture
def alternate_child_tree():
    """Returns a resource tree where sub-resources can be of multiple types.

    This implicitly tests the following parts of kalpa:

        - Child resource assignment to Branch classes
        - Child resource creation using the registered class
    """
    from kalpa import Root, Leaf

    class Root(Root):
        def __load__(self, name):
            if name in ('adam', 'eve'):
                return self._child(Admin, name)
            return self._child(name)

    class BadRoot(Root):
        def __load__(self, name):
            if name == 'explicit_none':
                return self._child(None, name)
            return self._child(name)

    class Admin(Leaf):
        pass

    @Root.child_resource
    class User(Leaf):
        pass

    return {
        'root': Root(None),
        'bad_root': BadRoot(None),
        'admin_cls': Admin,
        'user_cls': User}


class TestBasicResource(object):
    def test_sub_resource_type(self, basic_tree):
        """Leaf is an instance of the Leaf class, for context selection."""
        root = basic_tree['root']
        leaf = root['leaf']
        assert isinstance(leaf, basic_tree['leaf_cls'])

    def test_sub_resource_lineage(self, basic_tree):
        """Leaf is a child resource of Root according to Pyramid lineage."""
        from pyramid.location import inside
        root = basic_tree['root']
        leaf = root['leaf']
        assert inside(leaf, root)

    def test_keyerror_for_nonexistant_sub_resource(self, basic_tree):
        root = basic_tree['root']
        with pytest.raises(KeyError):
            root['nonexistant']

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
        from pyramid.location import inside
        root = branching_tree['root']
        leaf = root['objects']['any']
        assert inside(leaf, root)
        assert inside(leaf, root['objects'])

    def test_alternate_object_lineage(self, branching_tree):
        """Objects from collection is in lineage of Root and Collection."""
        from pyramid.location import inside
        root = branching_tree['root']
        leaf = root['people']['bob']
        assert inside(leaf, root)
        assert inside(leaf, root['people'])

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


class TestAlternateResourceClasses(object):
    def test_common_child_resource(self, alternate_child_tree):
        """"Retrieves an instance of the associated child class."""
        root = alternate_child_tree['root']
        assert type(root['john']) is alternate_child_tree['user_cls']

    def test_alternate_child_resource(self, alternate_child_tree):
        """Retrieves an instance of a loader-selected resource class."""
        root = alternate_child_tree['root']
        assert type(root['eve']) is alternate_child_tree['admin_cls']

    def test_missing_child_resource(self, alternate_child_tree):
        root = alternate_child_tree['bad_root']
        with pytest.raises(TypeError) as excinfo:
            root['adam']
        # Check for the more informative message for the bad-config case
        assert 'No child resource class is associated' in str(excinfo.value)
        assert 'not callable' not in str(excinfo.value)

    def test_bad_child_resource_class(self, alternate_child_tree):
        root = alternate_child_tree['bad_root']
        with pytest.raises(TypeError) as excinfo:
            root['explicit_none']
        # Check for the default Python non-callable error message
        assert 'not callable' in str(excinfo.value)


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


class TestPyramidTraversalIntegration(object):
    def test_find_root(self, branching_tree):
        """For a given resource, Pyramid can find its root."""
        from pyramid.traversal import find_root
        root = branching_tree['root']
        assert find_root(root) == root
        assert find_root(root['people']['alice']) == root
        assert find_root(root['objects']['egg']['votes']) == root

    def test_find_resource(self, branching_tree):
        """Resolving paths yields the expected resource."""
        from pyramid.traversal import find_resource
        root = branching_tree['root']
        bob = root['people']['bob']
        pvotes = root['objects']['peach']['votes']
        assert find_resource(root, '/') == root
        assert find_resource(root, '/people/bob') == bob
        assert find_resource(root, '/objects/peach/votes') == pvotes

    def test_resource_path(self, branching_tree):
        """Resources generate the expected path."""
        from pyramid.traversal import resource_path
        root = branching_tree['root']
        person_eve = root['people']['eve']
        votes_pear = root['objects']['pear']['votes']
        assert resource_path(person_eve) == '/people/eve'
        assert resource_path(votes_pear) == '/objects/pear/votes'

    def test_resource_path_aliased(self, basic_tree):
        """Finds a resource by its aliases and verifies the canonical path."""
        from pyramid.traversal import find_resource, resource_path
        root = basic_tree['root']
        for path in ('leaf', 'leaves', 'foliage'):
            resource = find_resource(root, (path,))
            assert resource_path(resource) == '/leaf'


def test_separate_subpath_registries(basic_tree, branching_tree):
    """Verify that subpath registries are not shared between classes."""
    basic_root = basic_tree['root_cls']
    branching_root = branching_tree['root_cls']
    assert basic_root._SUBPATHS is not branching_root._SUBPATHS


def test_util_lineage(branching_tree):
    """Assures that kalpa's lineage function works similarly to Pyramid's."""
    from kalpa import util
    from pyramid import location
    edmund = branching_tree['root']['people']['edmund']
    assert list(location.lineage(edmund)) == list(util.lineage(edmund))


def test_find_parent_by_class(branching_tree):
    """Finding a parent resource by its class or class name."""
    from kalpa.util import parent_by_class
    root = branching_tree['root']
    adam = root['people']['adam']
    selectors_result_mapping = [
        ((branching_tree['person_cls'], 'Person'), adam),
        ((branching_tree['people_cls'], 'People'), root['people']),
        ((branching_tree['root_cls'], 'Root'), root)]
    for selectors, result in selectors_result_mapping:
        for selector in selectors:
            assert parent_by_class(adam, selector) is result


def test_find_parent_by_class_no_match(branching_tree):
    """If no parent matches the given class, finder raises LookupError."""
    from kalpa.util import parent_by_class
    with pytest.raises(LookupError):
        parent_by_class(branching_tree['root'], object)
    with pytest.raises(LookupError):
        parent_by_class(branching_tree['root'], 'Singleton')


def test_find_parent_by_name(branching_tree):
    """Finding a parent resource by its resource name."""
    from kalpa.util import parent_by_name
    root = branching_tree['root']
    apple_votes = root['objects']['apple']['votes']
    assert parent_by_name(apple_votes, 'votes') is apple_votes
    assert parent_by_name(apple_votes, 'apple') is root['objects']['apple']
    assert parent_by_name(apple_votes, 'objects') is root['objects']
    assert parent_by_name(apple_votes, None) is root


def test_find_parent_by_name_no_match(branching_tree):
    """If no parent matches the given name, finder raises LookupError."""
    from kalpa.util import parent_by_name
    with pytest.raises(LookupError):
        parent_by_name(branching_tree['root'], 'olive')
