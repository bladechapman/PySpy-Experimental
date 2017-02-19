import inspect
import operator
from functools import reduce


def chained_hasattr(obj, prop_str):
    properties = prop_str.split(".")
    if properties == [""]:
        return obj

    for p in properties:
        if hasattr(obj, p):
            obj = getattr(obj, p)
        else:
            return False
    return True

def chained_getattr(obj, prop_str, oget=False):
    properties = prop_str.split(".")
    if properties == [""]:
        return obj

    for p in properties:
        if hasattr(obj, p):
            # obj = getattr(obj, p)
            if oget == True:
                obj = obj._oget(p)
            else:
                obj = getattr(obj, p)
        else:
            raise AttributeError(obj, "does not have attribute", prop_str)
    return obj

def chained_setattr(obj, prop_str, value):
    properties = prop_str.split(".")

    for p in properties[:-1]:
        if hasattr(obj, p):
            obj = getattr(obj, p)
        else:
            raise AttributeError(obj, "does not have attribute", prop_str)
    object.__setattr__(obj, properties[-1], value)
    # setattr(obj, properties[-1], value)

def is_bound_method(f):
    return hasattr(f, "__self__")

def is_handler(f):
    if is_bound_method(f):
        f = f.__func__
    return hasattr(f, "_observing")

def top_sort(node, ordering, init_val, observed):
    if node.__name__ not in observed:
        return

    if init_val > ordering[node.__name__]:
        ordering[node.__name__] = init_val

    for h in observed[node.__name__]:
        top_sort(h, ordering, init_val + 1, observed)




def add_marked(obj):
    if not hasattr(obj, "marked"):
        object.__setattr__(obj, "marked", dict())

def gather_obj_observations(obj):
    unmodified_handler_functions = [(i, j) for (i, j) \
        in inspect.getmembers(obj, inspect.ismethod) \
        if is_handler(j)]

    # gather observed attributes
    observed = dict()
    observed_mode = dict()
    for n, h in unmodified_handler_functions:
        for t in h._observing:
            if t not in observed:
                observed[t] = set()
            observed[t].add(h)
            observed_mode[t] = h._observing[t]["mode"]

    return observed, observed_mode

def gather_root_observed(obj, observed, observed_mode):
    observed_functions = {i:observed[i] \
        for i in observed \
        if observed_mode[i] != "deferred" \
        and callable(chained_getattr(obj, i))}
    observed_attributes = {i:observed[i] \
        for i in observed \
        if observed_mode[i] != "deferred" \
        and not callable(chained_getattr(obj, i))}
    root_observed_functions = {}
    for func_name in observed_functions:
        should_add = False
        if is_handler(chained_getattr(obj, func_name)):
            handler_observing = chained_getattr(obj, func_name)._observing
            statuses = map(lambda x: observed_mode[x] == "deferred", handler_observing)
            should_add = reduce(lambda x, y: x and y, statuses, True)
        else:
            should_add = True

        if should_add:
            root_observed_functions[func_name] = observed_functions[func_name]
    root_observed = {i:observed[i] \
        for i in observed \
        if i in root_observed_functions \
        or i in observed_attributes}

    return root_observed

def build_ordering_for_root_observed(root_observed):
    ordering = {i:0for i in root_observed}
    for i in root_observed:
        for h in root_observed[i]:
            top_sort(h, ordering, 1, root_observed)
    ordering = sorted(ordering.items(), key=operator.itemgetter(1))
    return ordering

def setup_marked(obj, full_str, final_handlers):
    # add item to marked
    components = full_str.split(".")
    if components[0] not in obj.marked:
        obj.marked[components[0]] = dict()
    if full_str not in obj.marked[components[0]]:
        obj.marked[components[0]][full_str] = set()

    obj.marked[components[0]][full_str] = \
        obj.marked[components[0]][full_str].union(final_handlers)


    if len(components) > 1 and hasattr(obj, components[0]):
        setup_marked(getattr(obj, components[0]), ".".join(components[1:]), final_handlers)
