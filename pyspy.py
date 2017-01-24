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

def is_handler(f):
    if is_bound_method(f):
        f = f.__func__
    return hasattr(f, "_observing")




def observe(observable):
    def wrap(handler):
        nonlocal observable
        if not isinstance(observable, Observable):
            raise TypeError("Given observable must be instance of Observable")

        # retrieve the underlying function
        f = None
        if isinstance(handler, ObservableFunction):
            f = handler.__func__
        else:
            f = handler

        # if not handler, promote
        if not is_handler(f):
            f._observing = dict()

        # build link, no double registering
        f._observing[observable] = {"type": "reference"}
        observable.register_handler(handler)

        return handler
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





class Observable(object):
    def __init__(self):
        self._handlers = set()

    def register_handler(self, f):
        self._handlers.add(f)


class ObservableFunction(Observable):
    def __init__(self, f):
        super().__init__()
        self.__func__ = f

        if is_handler(self.__func__):
            for observee in self.__func__._observing:
                observee._handlers.remove(self.__func__)
                observee._handlers.add(self)

    def __call__(self):
        returned_value = self.__func__()
        # invoke _handlers
        for handler in self._handlers:
            handler()


class ObservableValue(Observable):
    def __init__(self, value):
        super().__init__()
        self.__value = value

    def get(self):
        return self.__value

    def set(self, value):
        self.__value = value

        # invoke _handlers
        for handler in self._handlers:
            handler()
