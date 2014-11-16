
import itertools


def is_dict(obj):
    """Checks if obj is dict-like

    Dicts should have an iteriterms method"""
    try:
        obj.items
        obj.iteritems
    except AttributeError:
        return False


def is_string(obj):
    """Checks if obj is string-like

    Strings should be able to be concatenated with strings"""
    try:
        obj + ''
        return True
    except TypeError:
        return False


def is_iterable(obj):
    """Checks if obj is list-like without exhausting too much of a generator

    Iterables should be able to accept a slice item"""
    try:
        obj[:0]
        return True
    except TypeError:
        return False


def auto_iterate(obj):
    """Builds a consistent traversing mechanism from obj

    Returns
    -------
    container
        Destination object
    adder : method(container, key, value)
        Method of container that adds each item. Returns the updated container
    iterator : iterator
        Has the (key, value) pairs that should be passed to adder
    """
    if is_dict(obj):
        container = {}

        def adder(container, key, value):
            container[key] = value
            return container
        iterator = obj.iteritems()
    elif is_string(obj):
        # Return same object if string
        container = obj

        def adder(container, key, value):
            return value
        iterator = dict(s=obj).iteritems()
    elif is_iterable(obj):
        container = []

        def adder(container, key, value):
            container.append(value)
            return container
        iterator = itertools.izip_longest([], obj)
    else:
        # Return same object
        container = obj

        def adder(container, key, value):
            return value
        iterator = dict(s=obj).iteritems()
    return container, adder, iterator
