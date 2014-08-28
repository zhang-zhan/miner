__author__ = 'Peter_Howe<haobibo@gmail.com>'

import collections

class OrderedDefaultDict(collections.OrderedDict):
    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.iteritems()



class Map(object):
    """ Map wraps a dictionary. It is essentially an abstract class from which
    specific multimaps are subclassed. """
    def __init__(self,ordered=False):
        self._dict = collections.OrderedDict() if ordered else {}

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self._dict))

    __str__ = __repr__

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def remove(self, key, value):
        del self._dict[key]

    def dict(self):
        """ Allows access to internal dictionary, if necessary. Caution: multimaps
        will break if keys are not associated with proper container."""
        return self._dict

    def __len__(self):
        return len(self._dict)

    def iteritems(self):
        return self._dict.iteritems()

    def get(self, key, default):
        return self._dict.get(key, default)


class ListMultimap(Map):
    """ ListMultimap is based on lists and allows multiple instances of same value. """
    def __init__(self,ordered=False):
        self._dict = OrderedDefaultDict(list) if ordered else collections.defaultdict(list)

    def __setitem__(self, key, value):
        self._dict[key].append(value)

    def remove(self, key, value):
        self._dict[key].remove(value)



class SetMultimap(Map):
    """ SetMultimap is based on sets and prevents multiple instances of same value. """
    def __init__(self,ordered=False):
        self._dict = OrderedDefaultDict(set) if ordered else collections.defaultdict(set)

    def __setitem__(self, key, value):
        self._dict[key].add(value)

    def remove(self, key, value):
        self._dict[key].remove(value)



class DictMultimap(Map):
    """ DictMultimap is based on dicts and allows fast tests for membership. """
    def __init__(self,ordered=False):
        self._dict = OrderedDefaultDict(ordered) if ordered else collections.defaultdict(dict)

    def __setitem__(self, key, value):
        self._dict[key][value] = True

    def remove(self, key, value):
        del self._dict[key][value]
