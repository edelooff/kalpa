"""Kalpa helper utilities."""

import functools


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
