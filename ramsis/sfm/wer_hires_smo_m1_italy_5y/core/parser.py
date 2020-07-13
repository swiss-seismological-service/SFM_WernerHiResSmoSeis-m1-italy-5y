"""
Default parameter population resources for mapping of
configuration and input data to that expected by model adaptor.
"""
# Remove if not required: Class to combine multiple
# parameter dictionaries. (Created for HM1)
# If the model_adaptor ChainMap usage doesn't work for your case,
# It is possible to implement something like this. For the HM1
# implementation, a ChainMap was not good enough as the parameter
# 'tree' had more than two levels and also required in place
# modifications which ChainMap does not allow.

from collections import abc


# This class builds upon the Chainmap class described here:
# http://code.activestate.com/recipes/305268/.
# It provides an elegant way to merge multiple hierarchical dictionaries or
# other mapping-type objects in Python.


class ChainMapTree(dict, abc.Mapping):
    """Combine/overlay multiple hierarchical mappings. This efficiently merges
    multiple hierarchical (could be several layers deep) dictionaries, gives
    a new view into them that acts exactly like a merged dictionary, without
    doing any copying.
    Because it doesn't actually copy the data, it is intended to be used only
    with immutable mappings. It is safe to change *leaf* data values,
    and the results will be reflected here, but changing the structure of any
    of the trees will not work.
    """
    def __init__(self, *maps):
        _maps = list(maps)

        # All keys of kids that are mappings
        kid_keys = set([key for m in maps
                        for key in m.keys() if
                        isinstance(m[key], abc.Mapping)])

        # This will be a dictionary of lists of mappings
        kid_maps = {}
        for key in kid_keys:
            # The list of child mappings for this key
            kmaps = [m[key] for m in maps if key in m]
            # Make sure they are *all* mappings
            if any(not isinstance(i, abc.Mapping) for i in kmaps):
                raise KeyError(key)
            # Recurse
            kid_maps[key] = ChainMapTree(*kmaps)

        # If non-empty, prepend it to the existing list
        if len(kid_maps.keys()) > 0:
            _maps.insert(0, kid_maps)

        self._maps = _maps

    def get(self, key, default=None):
        retval = self.__getitem__(key, default)
        return retval if retval else default

    def __getitem__(self, key, default=None):
        new_map_list = []
        for i, mapping in enumerate(self._maps):
            try:
                retval = mapping[key]
                if isinstance(retval, ChainMapTree):
                    new_map_list.extend(retval._maps)
                elif isinstance(retval, dict):
                    new_map_list.append(retval)
                else:
                    return retval
            except KeyError:
                pass
        if new_map_list:
            return ChainMapTree(*new_map_list)
        if default:
            return default
        else:
            raise KeyError(key)

    def __setitem__(self, key, item):
        use_map = self._maps[0]
        use_map.__setitem__(key, item)

    def __iter__(self):
        return self._maps.__iter__()

    def __len__(self):
        return self._maps.__len__()
