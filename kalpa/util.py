"""Kalpa helper utilities."""

import functools


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
    if isinstance(parent_cls, type):
        return _find_parent(resource, lambda res: type(res) is parent_cls)
    return _find_parent(resource, lambda res: type(res).__name__ == parent_cls)


def _find_parent(child_resource, predicate):
    """Returns resource's first parent that fulfills the predicate function."""
    for resource in lineage(child_resource):
        if predicate(resource):
            return resource
    raise LookupError('No matching parent in resource lineage.')
