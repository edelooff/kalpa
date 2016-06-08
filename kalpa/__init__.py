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

    def __getitem__(self, path):
        """Return the requested child instance or raise KeyError."""
        if path in self.__children__:
            return self.__children__[path]
        if self._SUBPATHS is None:
            raise KeyError(path)
        resource_class, name = self._SUBPATHS[path]
        return self._create_and_cache_child(resource_class, name, path)

    def _sprout(self, _name, **attrs):
        """Creates and returns a child resource of the type registered."""
        return self._create_and_cache_child(
            self._CHILD_CLS, _name, _name, attrs=attrs)

    def _sprout_resource(self, _resource_cls, _name, **attrs):
        """Adds a child resource of the provided type, with given name."""
        return self._create_and_cache_child(
            _resource_cls, _name, _name, attrs=attrs)

    def _create_and_cache_child(self, resource_cls, name, path, attrs=None):
        """Adds a child resource to a subpath.

        The resource class is created from the canonical path (name) and added
        to the provided path segment. Additional keyword arguments are used to
        instantiate the resource class with.

        After creation, the resource is added to the __children__ cache for
        future retrieval, ensuring consistent lineage for Pyramid usage.
        """
        if attrs is None:
            attrs = {}
        resource = resource_cls(name, self, **attrs)
        self.__children__[path] = resource
        return resource

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
    def child_resource(cls):
        """Adds a resource class as the default child resource to sprout."""
        cls._CHILD_RESOURCE = cls
        return cls


class Root(Branch):
    """Basic traversal root class to catch the initial request."""
    def __init__(self, request):
        """Initialize the Root resource and have the request stored."""
        super(Root, self).__init__(None, None, request=request)