from functools import wraps
import inspect

#TODO: Build chained hasattr for decorator
#TODO: Build in observation of function attributes

def chained_hasattr(obj, prop_str):
    properties = prop_str.split(".")
    for p in properties:
        if hasattr(obj, p):
            obj = getattr(obj, p)
        else:
            return False
    return True

def chained_getattr(obj, prop_str):
    properties = prop_str.split(".")
    for p in properties:
        if hasattr(obj, p):
            obj = getattr(obj, p)
        else:
            raise AttributeError(obj, "does not have attribute", prop_str)
    return obj

def observe(prop_str):
    def wrap(f):
        if not hasattr(f, "__observed_attributes"):
            f.__observed_attributes = set()
        f.__observed_attributes.add(prop_str)
        return f
    return wrap


class PySpyBase(object):
    def __init__(self):
        self.registered_attributes = dict()

        handler_functions = \
            ((i, j) for (i, j) in inspect.getmembers(self, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)

        for f_name, handler in handler_functions:
            for attribute_name in getattr(handler, "__observed_attributes"):

                if attribute_name not in self.registered_attributes:
                    self.registered_attributes[attribute_name] = []
                self.registered_attributes[attribute_name].append((f_name, handler))

                # # TODO: Allow default initial value to be specified in decorator
                # if not hasattr(self, attribute_name):
                #     setattr(self, attribute_name, None)
                # value = getattr(self, attribute_name)

    def __setattr__(self, name, value):
        if not hasattr(self, "registered_attributes") or \
            name not in super().__getattribute__("registered_attributes"):
            return super().__setattr__(name, value)
        else:
            for f_name, handler in super().__getattribute__("registered_attributes")[name]:
                handler()
            return super().__setattr__(name, value)
