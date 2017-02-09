
def chained_getattr(obj, prop_str):
    properties = prop_str.split(".")
    if properties == [""]:
        return obj

    for p in properties:
        if hasattr(obj, p):
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
    setattr(obj, properties[-1], value)

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
