from functools import wraps
import inspect
import gc

#TODO: Fix ignore
#TODO: Add ability to specify handler priority
#TODO: Build in observation of collection attributes (dicts, arrays, ...)
#TODO: Clean this code up a bit...

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

def is_bound_method(f):
    return hasattr(f, "__self__")

def observe(prop_str=None):
    def wrap(f):
        if is_bound_method(f):
            g = f.__func__
            if not hasattr(g, "__observed_attributes"):
                g.__observed_attributes = set()
            if prop_str is not None and prop_str not in g.__observed_attributes:
                g.__observed_attributes.add(prop_str)
            return f
        else:
            if not hasattr(f, "__observed_attributes"):
                f.__observed_attributes = set()
            if prop_str is not None and prop_str not in f.__observed_attributes:
                f.__observed_attributes.add(prop_str)
            return f
    return wrap

# This needs to take an instance as a param
# Modify the current instance's observation, as well as the instance where the
# original property is being looked at
def ignore(prop_str, f, instance):
    pass
    # if not isinstance(instance, Observable):
    #     raise TypeError("Properties can only be ignored on instance of Observable")
    #
    # if hasattr(f, "__observed_attributes"):
    #     if prop_str in f.__observed_attributes:
    #         f.__observed_attributes.remove(prop_str)
    #
    # prop_components = prop_str.split(".")
    # obj = chained_getattr(instance, ".".join(prop_components[:-1]))
    # Observable.reveal(obj)


def observed_function(f):
    @wraps(f)
    def modified_function(self, *args, **kwargs):
        print("MODIFIED FUNCTION CALLED", f)
        result = f(*args, **kwargs)
        if f.__name__ in self.registered_attributes:
            for f_name, obj, registered_name in self.registered_attributes[f.__name__]:
                handler = getattr(obj, f_name)
                if not callable(handler):
                    raise Exception("Handler not callable")
                handler(values={registered_name:result})

    modified_function.__handler__ = True
    return modified_function


class Observable(object):
    @staticmethod
    def reveal(instance):
        instance.registered_attributes = dict()

        # Look for observed functions and overwrite them using observable_function
        # decorator
        original_handlers = \
            ((i, j) for (i, j) in inspect.getmembers(instance, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)
        for f_name, handler in original_handlers:
            for prop_str in getattr(handler, "__observed_attributes"):
                prop_components = prop_str.split(".")
                obj = chained_getattr(instance, ".".join(prop_components[:-1]))
                prop = prop_components[-1]

                if not isinstance(obj, Observable):
                    raise TypeError("Object not observable")

                # Handle bound functions
                if callable(getattr(obj, prop)) and \
                    not hasattr(getattr(obj, prop), "__handler__"):
                    f = observed_function(getattr(obj, prop))
                    bound_f = f.__get__(obj, type(obj))
                    object.__setattr__(obj, prop, bound_f)

        # Register the handlers, using the overwritten bound functions
        handlers = \
            ((i, j) for (i, j) in inspect.getmembers(instance, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)
        for f_name, handler in handlers:
            for prop_str in getattr(handler, "__observed_attributes"):
                prop_components = prop_str.split(".")
                obj = chained_getattr(instance, ".".join(prop_components[:-1]))
                prop = prop_components[-1]

                if not isinstance(obj, Observable):
                    raise TypeError("Object not observable")

                # Register the property
                if prop not in obj.registered_attributes:
                    obj.registered_attributes[prop] = set()
                obj.registered_attributes[prop].add((f_name, instance, prop_str))

    @staticmethod
    def conceal(instance):
        instance.registered_attributes = dict()

    def __setattr__(self, name, value):
        if not hasattr(self, "registered_attributes") or \
            name not in super().__getattribute__("registered_attributes"):
            return super().__setattr__(name, value)
        else:
            r = super().__setattr__(name, value)
            for f_name, obj, registered_name in super().__getattribute__("registered_attributes")[name]:
                handler = getattr(obj, f_name)
                if not callable(handler):
                    raise Exception("Handler not callable")
                handler(values={registered_name:getattr(self, name)})


            return r
