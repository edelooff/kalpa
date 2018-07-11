"""Kalpa provides base classes for Pyramid's traversal mechanism."""

from itertools import chain

from six import (
    iteritems,
    with_metaclass)

from .util import (
    lineage,
    memoize,
    register_resource,
    resolve_resource)


class DeclaredBranch(object):
    """Used for declarative attachment of resource tree nodes.

    This takes the class name of the node that should be created. Aliases can
    be provided as alternate names that the resource can be accessed through.
    Aliased paths can be accessed as normal, but resource_path functions from
    Pyramid's traversal machinery will return the canonical name.
    """
    def __init__(self, resource_name, aliases=(), branching_cls=None):
        self.resource_name = resource_name
        self.aliases = aliases
        self._branching_cls = branching_cls or Brancher

    def generate_resources(self, attr):
        """Yields 2-tuples of path and Brancher instances.

        The retured paths are the canonical path (from the attr parameter), as
        well as all aliases that have been configured. The Brancher instance
        is shared across all 2-tuples.
        """
        resource = self._branching_cls(self.resource_name, attr)
        return ((path, resource) for path in chain([attr], self.aliases))


class Brancher(object):
    """Used to generate the branching nodes used for tree traversal.

    A Brancher is usually stored in a class' branch registry, and when a
    registered path is accessed, the Brancher retrieves the associated resource
    class from the registry and from it, creates the next Node for traversal.
    """
    def __init__(self, node_cls, path):
        """Initalizes the Brancher based on the given node class and path.

        The node class provided may be a class, the name of a registered class,
        or a callable that resolves to a class.
        The path provided will be used to instantiate the node with, and
        determines the resource_path as returned by Pyramid utility functions.
        """
        self._node_cls = node_cls
        self._path = path

    def __call__(self, parent):
        """Returns a resolved and instantiated node, with the given parent."""
        return self.node_cls(self._path, parent)

    @property
    def node_cls(self):
        """Returns the resolved resource class to build the branch."""
        return resolve_resource(self._node_cls)


def branch(resource, **kwds):
    return DeclaredBranch(resource, **kwds)


class NodeMeta(type):
    """Sets up the declarative branch registry for each Node class.

    Also registers non-abstract classes in the shared resource registry.
    """
    def __new__(mcs, name, bases, attrs):
        should_register = not attrs.pop('__abstract__', False)
        attributes = {'__child_cls__': None}
        branches = attributes['_BRANCHES'] = {}
        for attr, value in attrs.iteritems():
            if isinstance(value, DeclaredBranch):
                branches.update(value.generate_resources(attr))
            else:
                attributes[attr] = value

        # Create the class and register it for declarative attachment
        klass = super(NodeMeta, mcs).__new__(mcs, name, bases, attributes)
        if should_register:
            register_resource(klass)
        return klass


class Node(with_metaclass(NodeMeta, object)):
    """Describes a node in the resource tree."""
    __abstract__ = True

    def __init__(self, _name, _parent, **attributes):
        self.__name__ = _name
        self.__parent__ = _parent
        self.__attributes__ = attributes
        for attr, value in iteritems(attributes):
            setattr(self, attr, value)

    def __getattr__(self, attr):
        """Returns attribute from this resource or one of its ancestors.

        To prevent inadvertent method or private attribute access, only the
        optional keywords provided at initialization time are checked.
        """
        for resource in lineage(self):
            if attr in resource.__attributes__:
                value = self.__dict__[attr] = resource.__attributes__[attr]
                return value
        raise AttributeError(
            '{!r} object has no attribute {!r}'.format(self, attr))

    @memoize
    def __getitem__(self, path):
        """Returns a cached child resource or returns a newly created one.

        If the requested path is in the cache, the cached value is returned.
        Failing that, a check is done for statically attached resources. If one
        is found, it's instantiated, cached, and returned.

        A final attempt to load a resource is made by calling out to __load__.
        If this succeeds, the result is cached and returned.
        """
        if path in self._BRANCHES:
            return self._BRANCHES[path](self)
        resource = self.__load__(path)
        if isinstance(resource, dict):
            return self._child_from_dict(path, resource)
        return resource

    def __load__(self, name):
        """Dynamic resource loader for custom Node classes.

        This method should either raise a KeyError or return an instantiated
        resource class. This can be achieved with the _child() method or manual
        instantiation. The response will be cached by __getitem__().
        """
        raise KeyError(name)

    def __repr__(self):
        """Returns a simple resources representation."""
        return '<{}>'.format(type(self).__name__)

    def _child(self, resource_class, path, **attrs):
        """Returns a newly instantiated child resource.

        The resource class can be either the class itself, the name of a Node
        subclass, or a function returning the resource class.

        Additional named parameters are passed verbatim to the new instance.
        """
        resource_class = resolve_resource(resource_class)
        return resource_class(path, self, **attrs)

    def _child_from_dict(self, path, resource_params):
        if self.__child_cls__ is None:
            raise TypeError(
                'A child resource class (__child_cls__) should be defined '
                'when using dict-like returns for __load__(). ')
        return self._child(self.__child_cls__, path, **resource_params)

    # #########################################################################
    # Deprecated methods for implicit tree construction
    #
    @classmethod
    def attach(cls, canonical_path, aliases=()):
        """Adds a resource as the child of another resource."""
        def _attach_resource(child_cls):
            """Stores the sub-resource on all relevant paths."""
            for path in [canonical_path] + list(aliases):
                cls._BRANCHES[path] = Brancher(child_cls, canonical_path)
            return child_cls
        return _attach_resource

    @classmethod
    def child_resource(cls, child_cls):
        """Adds a resource class as the default child class to instantiate."""
        cls.__child_cls__ = child_cls
        return child_cls


class Root(Node):
    """Basic traversal root class to catch the initial request."""
    __abstract__ = True

    def __init__(self, request):
        """Initialize the Root resource and have the request stored."""
        super(Root, self).__init__(None, None, request=request)
