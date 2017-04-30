"""Kalpa provides base classes for Pyramid's traversal mechanism."""

from six import (
    iteritems,
    with_metaclass)

from .util import (
    lineage,
    memoize)


class Leaf(object):
    """Base resource class for an end-node."""
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

    def __repr__(self):
        """Returns a simple resources representation."""
        return '<{}>'.format(type(self).__name__)


class BranchType(type):
    """Provide each class with its own unshared subpath registry."""
    def __init__(cls, name, bases, namespace):
        super(BranchType, cls).__init__(name, bases, namespace)
        cls._CHILD_CLS = None
        cls._SUBPATHS = {}


class Branch(with_metaclass(BranchType, Leaf)):
    """Base resource class for a branch, extends Leaf."""

    @memoize
    def __getitem__(self, path):
        """Returns a cached child resource or returns a newly created one.

        If the requested path is in the cache, the cached value is returned.
        Failing that, a check is done for statically attached resources. If one
        is found, it's instantiated, cached, and returned.

        A final attempt to load a resource is made by calling out to __load__.
        If this succeeds, the result is cached and returned.
        """
        if self._SUBPATHS is not None and path in self._SUBPATHS:
            resource_class, name = self._SUBPATHS[path]
            return resource_class(name, self)
        return self.__load__(path)

    def __load__(self, path):
        """Dynamic resource loader for custom Branch classes.

        This method should either raise a KeyError or return an instantiated
        resource class. This can be achieved with the _child() method or manual
        instantiation. The response will be cached by __getitem__().
        """
        raise KeyError(path)

    def _child(self, *args, **attrs):
        """Returns a newly instantiated child resource.

        Positional arguments are either type+name or just a name. If the type
        is not given, this defaults to the registered child resource class.

        Additional named parameters are passed verbatim to the new instance.
        """
        if len(args) == 1:
            if self._CHILD_CLS is None:
                raise TypeError(
                    'No child resource class is associated with %r. '
                    'Provide one as the first argument' % self)
            resource_class = self._CHILD_CLS
            name, = args
        else:
            resource_class, name = args
        return resource_class(name, self, **attrs)

    @classmethod
    def attach(cls, canonical_path, aliases=()):
        """Adds a resource as the child of another resource."""
        def _attach_resource(child_cls):
            """Stores the sub-resource on all relevant paths."""
            for path in [canonical_path] + list(aliases):
                cls._SUBPATHS[path] = child_cls, canonical_path
            return child_cls
        return _attach_resource

    @classmethod
    def child_resource(cls, child_cls):
        """Adds a resource class as the default child class to instantiate."""
        cls._CHILD_CLS = child_cls
        return child_cls


class Root(Branch):
    """Basic traversal root class to catch the initial request."""
    def __init__(self, request):
        """Initialize the Root resource and have the request stored."""
        super(Root, self).__init__(None, None, request=request)
