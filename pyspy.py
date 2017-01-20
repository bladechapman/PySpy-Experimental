from functools import wraps
import inspect

#TODO: Build in observation of function attributes
#TODO: Build in observation of collection attributes (dicts, arrays, ...)

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

def observe(prop_str):
    def wrap(f):
        if not hasattr(f, "__observed_attributes"):
            f.__observed_attributes = []
        f.__observed_attributes.append(prop_str.split("."))
        return f
    return wrap


class PySpyBase(object):
    def __init__(self):
        self.registered_attributes = dict()

        handler_functions = \
            ((i, j) for (i, j) in inspect.getmembers(self, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)

        for f_name, handler in handler_functions:
            for prop_str in getattr(handler, "__observed_attributes"):
                obj = chained_getattr(self, ".".join(prop_str[:-1]))
                prop = prop_str[-1]

                if prop not in obj.registered_attributes:
                    obj.registered_attributes[prop] = []
                obj.registered_attributes[prop].append((f_name, handler))

                # # TODO: Allow default initial value to be specified in decorator
                # if not hasattr(self, prop_str):
                #     setattr(self, prop_str, None)
                # value = getattr(self, prop_str)

    def __setattr__(self, name, value):
        if not hasattr(self, "registered_attributes") or \
            name not in super().__getattribute__("registered_attributes"):
            return super().__setattr__(name, value)
        else:
            r = super().__setattr__(name, value)
            for f_name, handler in super().__getattribute__("registered_attributes")[name]:
                handler()
            return r
