"""Kalpa helper utilities."""

import functools

# Registry for resource classes
_RESOURCE_REGISTRY = {}


def inherited_branches(bases):
    """Returns a dictionary of combined branches for all the given bases.

    Bases are evaluated in reverse order (right to left), mimicking Python's
    method resolution order. This means that branches defined on multiple
    bases will take the value from the leftmost base.
    """
    branches = {}
    for base in reversed(bases):
        branches.update(getattr(base, '_BRANCHES', {}))
    return branches


def lineage(resource):
    """Yields the resource's lineage up to the root.

    This is a copy of Pyramid's lineage function to reduce dependencies.
    It assumes that parent resources are correctly set (which kalpa does).
    """
    while resource is not None:
        yield resource
        resource = resource.__parent__


def memoize(wrapped):
    """Caches values returned by method, storing a cache on the instance.

    The name cache is based on the function name, preventing accidental cache
    sharing when multiple functions are memoized.
    """
    cache_name = wrapped.__name__.rstrip('_') + '__cache'

    def decorator(inst, item):
        try:
            cache = getattr(inst, cache_name)
        except AttributeError:
            cache = {}
            setattr(inst, cache_name, cache)
        if item not in cache:
            cache[item] = wrapped(inst, item)
        return cache[item]
    return functools.update_wrapper(decorator, wrapped)


def parent_by_name(resource, parent_name):
    """Returns the first parent whose name matches the query."""
    return _find_parent(resource, lambda res: res.__name__ == parent_name)


def parent_by_class(resource, parent_cls):
    """Returns the first parent to match the given class (type or name)."""
    parent_cls = resolve_resource(parent_cls)
    return _find_parent(resource, lambda res: type(res) is parent_cls)


def register_resource(cls):
    """Adds a to the registry by its local name."""
    _RESOURCE_REGISTRY[cls.__name__] = cls


def resolve_resource(resource):
    """Returns the resouurce class that the given value contains.

    - If the given value is a class, this class will be returned immediately;
    - If the given value is a callable, the function result will be returned;
    - In other cases, the resource is assumed to be a string and the resource
      class will be looked up from the registry. If this fails, LookupError
      will be raised.

    Raising KeyError is avoided due to its specific meaning during traversal.
    """
    if isinstance(resource, type):
        return resource
    if callable(resource):
        return resource()
    try:
        return _RESOURCE_REGISTRY[resource]
    except KeyError:
        raise LookupError('no registry entry {!r}'.format(resource))


def _find_parent(child_resource, predicate):
    """Returns resource's first parent that fulfills the predicate function."""
    for resource in lineage(child_resource):
        if predicate(resource):
            return resource
    raise LookupError('No matching parent in resource lineage.')
