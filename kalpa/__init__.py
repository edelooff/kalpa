"""Kalpa provides base classes for Pyramid's traversal mechanism."""


class Leaf(object):
    """Base resource class for an end-node."""
    def __init__(self, _name, _parent, **attributes):
        self.__name__ = _name
        self.__parent__ = _parent
        self.__attributes__ = attributes
        for attr, value in attributes.iteritems():
            setattr(self, attr, value)

    def __getattr__(self, attr):
        """Returns attribute from this resource or one of its ancestors.

        To prevent inadvertent method or private attribute access, only the
        optional keywords provided at initialization time are checked.
        """
        resource = self.__parent__
        while resource is not None:
            if attr in resource.__attributes__:
                value = resource.__attributes__[attr]
                setattr(self, attr, value)
                return value
            resource = resource.__parent__
        raise AttributeError(
            '{!r} object has no attribute {!r}'.format(self, attr))

    def __repr__(self):
        """Returns a simple resources representation."""
        return '<{}>'.format(type(self).__name__)


class Branch(Leaf):
    """Base resource class for a branch, extends Leaf."""
    _CHILD_CLS = None
    _SUBPATHS = None

    def __init__(self, _name, _parent, **attributes):
        super(Branch, self).__init__(_name, _parent, **attributes)
        self.__children__ = {}

    def __contains__(self, path):
        """Returns whether or not the provided path is in the child cache."""
        return path in self.__children__

    def __getitem__(self, path):
        """Returns a cached child resource or returns a newly created one.

        If the requested path is in the cache, the cached value is returned.
        Failing that, a check is done for statically attached resources. If one
        is found, it's instantiated, cached, and returned.

        A final attempt to load a resource is made by calling out to __load__.
        If this succeeds, the result is cached and returned.
        """
        if path in self.__children__:
            return self.__children__[path]
        if self._SUBPATHS is not None and path in self._SUBPATHS:
            resource_class, name = self._SUBPATHS[path]
            resource = self.__children__[path] = resource_class(name, self)
            return resource
        resource = self.__children__[path] = self.__load__(path)
        return resource

    def __load__(self, path):
        """Dynamic resource loader for custom Branch classes.

        This method should either raise a KeyError or return an instantiated
        resource class. Through one of _sprout(), _sprout_resource() or manual
        instantiation. The response will be cached by the caller, __getitem__.
        """
        raise KeyError(path)

    def _sprout(self, _name, **attrs):
        """Returns a child resource of the registered type."""
        return self._CHILD_CLS(_name, self, **attrs)

    def _sprout_resource(self, _resource_cls, _name, **attrs):
        """Returns a child resource of the provided type, with given name."""
        return _resource_cls(_name, self, **attrs)

    @classmethod
    def attach(cls, canonical_path, aliases=()):
        """Adds a resource as the child of another resource."""
        if cls._SUBPATHS is None:
            cls._SUBPATHS = {}
        paths = [canonical_path]
        paths.extend(aliases)

        def _attach_resource(child_cls):
            """Stores the sub-resource on all relevant paths."""
            for path in paths:
                cls._SUBPATHS[path] = child_cls, canonical_path
            return child_cls
        return _attach_resource

    @classmethod
    def child_resource(cls, child_cls):
        """Adds a resource class as the default child resource to sprout."""
        cls._CHILD_CLS = child_cls
        return child_cls


class Root(Branch):
    """Basic traversal root class to catch the initial request."""
    def __init__(self, request):
        """Initialize the Root resource and have the request stored."""
        super(Root, self).__init__(None, None, request=request)
