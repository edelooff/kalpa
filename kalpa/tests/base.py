from kalpa import (
    Root,
    Node,
    branch)


ALIASED_NODES = 'leaf', 'leaves', 'foliage'
ADMINS = {
    'daniel': {'name': 'Daniel', 'role': 'Database admin'},
    'eve': {'name': 'Eve', 'role': 'Systems admin'}}
PEOPLE = {
    'alice': {'name': 'Alice', 'role': 'Developer'},
    'bob': {'name': 'Bob', 'role': 'Artist'},
    'charlie': {'name': 'Charlie', 'role': 'Manager'}}


class ChildNode(Node):
    # Defined before Root so that it can be referenced by name.
    pass


class Root(Root):
    leaf = branch('Leaf', aliases=('foliage', 'leaves'))
    objects = branch('ObjectCollection')
    path = branch('Path')
    people = branch('People')
    bad_loader = branch('BadLoader')

    by_class = branch(ChildNode)
    by_function = branch(lambda: ChildNode)
    by_name = branch('ChildNode')

    conditional_always = branch('ChildNode', predicate=lambda res: True)
    conditional_never = branch('ChildNode', predicate=lambda res: False)
    conditional_request = branch(
        'ChildNode', predicate=lambda res: res.request == 'conditional')

    base_branch = branch('BaseBranch')
    colored_branch = branch('ColoredBranch')
    diamond_branch = branch('DiamondBranch')


class BadLoader(Node):
    """A Node class that defined a __load__ method but no __child_cls__."""

    def __load__(self, name):
        return {'name': name}


class ObjectCollection(Node):
    """A resource to demonstrate basic loads of objects.

    Child resources get attributes `twice` that contain the accessed path
    portion twice, and a `len` that details the length of the accessed path.
    """
    __child_cls__ = 'Object'
    escape = branch('Specialty')

    def __load__(self, name):
        return {'twice': name * 2, 'len': len(name)}


class Path(Node):
    """A recursive structure to reflect a filesystem path or similar."""
    __child_cls__ = 'Path'

    def __load__(self, name):
        return {'lc': name.lower(), 'uc': name.upper()}


class People(Node):
    """A resource to demonstrate loading resources from an external resource.

    In this case, entries are loaded from a dict, but they could be from a
    database or anything else. Keys in the returned resource (name and role)
    are used to construct a Person  record from.
    """
    __child_cls__ = 'Person'

    def __load__(self, name):
        if name in ADMINS:
            return self._child(Admin, name, **ADMINS[name])
        return PEOPLE.get(name)


class Leaf(Node):
    """A generic leaf node, at the end of the tree."""


class Admin(Node):
    """A person that additionally has an administrative role."""
    databases = branch(
        'Specialty', predicate=lambda res: 'database' in res.role.lower())
    servers = branch(
        'Specialty', predicate=lambda res: 'systems' in res.role.lower())

    def __load__(self, name):
        return self._child(ChildNode, name)


class BaseBranch(Node):
    """Baseclass to test branch inheritance."""
    local = branch('BaseNode')
    shared = branch('BaseNode')


class BaseNode(Node):
    """Child node for the BaseBranch."""


class ColoredBranch(BaseBranch):
    """Subclassed node to test branch inheritance."""
    local = branch('ColoredNode')
    sub_only = branch('ColoredNode')


class ColoredNode(Node):
    """Child node for the ColoredBranch."""


class _DiamonBranch(Node):
    """Subclassed node to test diamond inheritance."""
    local = branch('DiamondNode')


class DiamondBranch(_DiamonBranch, ColoredBranch):
    """Subclassed node to test diamond inheritance."""


class DiamondNode(Node):
    """Child node for the DiamondBranch."""


class Person(Node):
    """A person that is part of a fictional system."""


class Object(Node):
    """A real or fictional object that can be voted on."""
    votes = branch('Votes')


class Specialty(Node):
    """A lonely branch of a resource typically returning other branches."""


class Votes(Node):
    """Tracks the number of votes on an object resource."""
