from functools import wraps
import inspect

def observe(prop_str):
    def wrap(f):
        if not hasattr(f, "__observed_attributes"):
            f.__observed_attributes = set()
        f.__observed_attributes.add(prop_str)
        return f
    return wrap


class PySpyBase(object):
    def __init__(self):
        self.registered_attributes = set()

        handler_functions = \
            ((i, j) for (i, j) in inspect.getmembers(self, inspect.ismethod) \
            if hasattr(j, "__observed_attributes") == True)

        for name, handler in handler_functions:
            for attribute_name in getattr(handler, "__observed_attributes"):

                # TODO: Handle situation where observed variables have
                # not been declared yet (so super can be moved to head)
                value = getattr(self, attribute_name)
                if isinstance(value, ObservableAttribute) == False:
                    setattr(self, attribute_name, ObservableAttribute(value))
                getattr(self, attribute_name).register_handler((name, handler))

                self.registered_attributes.add(attribute_name)

    # TODO: Validate / refactor these two functions
    def __getattribute__(self, name):
        if name == "registered_attributes" or \
            not hasattr(self, "registered_attributes") or \
            name not in super().__getattribute__("registered_attributes"):

            return super().__getattribute__(name)
        else:
            return super().__getattribute__(name).__get__()

    def __setattr__(self, name, value):
        # print("SET", name)
        if not hasattr(self, "registered_attributes") or \
            name not in super().__getattribute__("registered_attributes"):
            return super().__setattr__(name, value)
        else:
            return super().__getattribute__(name).__set__(value)


class ObservableAttribute(object):
    def __init__(self, value):
        self.value = value
        self.handlers = []

    def __get__(self):
        return self.value

    def __set__(self, value):
        self.value = value
        for i, j in self.handlers:
            j()

    def register_handler(self, handler):
        self.handlers.append(handler)
