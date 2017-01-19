from functools import wraps
import inspect

def observe(prop_str):
    def wrap(f):

        print("Register handler for", prop_str)
        if not hasattr(f, "__observed_attributes"):
            f.__observed_attributes = set()
        f.__observed_attributes.add(prop_str)

        @wraps(f)
        def observing(self, *args, **kwargs):

            print("Invoke handler function of", prop_str)
            #
            # value = getattr(self, prop_str)
            # if isinstance(value, ObservableAttribute) == False:
            #     setattr(self, prop_str, ObservableAttribute(value))
            # obs_val = getattr(self, prop_str)
            # obs_val.register_handler((prop_str, f, self, args, kwargs))
            # self.registered_attributes.add(prop_str)

        # observing.__flagged = True
        # return observing
        return f
    return wrap

# def setup(init):
#     @wraps(init)
#     def new_init(self, *args, **kwargs):
#         init(self, *args, **kwargs)
#         observed_functions = \
#             ((i, j) for (i, j) in inspect.getmembers(self, inspect.ismethod) \
#             if hasattr(j, "__flagged") == True)
#         for _, f in observed_functions:
#             f(internal_call=True)
#
#         print("SETUP AFTER")
#     return new_init


class PySpyBase(object):
    def __init__(self):
        self.registered_attributes = set()
        observed_functions = \
            ((i, j) for (i, j) in inspect.getmembers(self, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)


    def __getattribute__(self, name):
        if name in super().__getattribute__("registered_attributes"):
            return super().__getattribute__(name).__get__()
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "registered_attributes" or \
            name not in super().__getattribute__("registered_attributes"):
            return super().__setattr__(name, value)
        else:
            return super().__getattribute__(name).__set__(value)


# class ObservableAttribute(object):
#     def __init__(self, value):
#         self.value = value
#         self.observers = []
#
#     def __get__(self):
#         return self.value
#
#     def __set__(self, value):
#         self.value = value
#         for i, j, s, a, k in self.observers:
#             print("Invoke observer for", i)
#             j(s, *a, **k)
#
#     def register_handler(self, handler):
#         self.observers.append(handler)
