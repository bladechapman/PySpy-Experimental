from .helpers import *

# TODO: clean this up...
# def setup_default_test(self, n, v, full_str, handlers, untouched_str, untouched_obj):
#     if len(full_str.split(".")) != 1:
#         if isinstance(v, ContainsObservables):
#             add_default_handler_for(".".join(full_str.split(".")[1:]), v, handlers)
#
#         if hasattr(v, full_str.split(".")[1]):
#             setup_default_test(v, full_str.split(".")[1], getattr(v, full_str.split(".")[1]), ".".join(full_str.split(".")[1:]), handlers, untouched_str, untouched_obj)
#
#     # trigger handlers at root
#     else:
#         object.__setattr__(self, n, v)
#         for handler in handlers:
#
#             if not chained_hasattr(untouched_obj, untouched_str):
#                 handler(new={"name": untouched_str, "value": v}, old={"name":untouched_str, "value": None})
#             else:
#                 handler(new={"name": untouched_str, "value": v}, old={"name":untouched_str, "value": chained_getattr(untouched_obj, untouched_str)})
#
#
#
# def add_default_handler_for(string, obj, handlers):
#     components = string.split(".")
#
#     if isinstance(obj, ContainsObservables):
#         if components[0] not in obj.marked:
#             obj.marked[components[0]] = dict()
#
#         obj.marked[components[0]][string] = handlers
#
#         # see if this can be reduced...
#         if len(components) > 1 and hasattr(obj, components[0]):
#             add_default_handler_for(".".join(components[1:]), object.__getattribute__(obj, components[0]), handlers)


def create_observable_from_value(v):
    if callable(v):
        return ObservableFunction(v)
    else:
        return ObservableValue(v)


# is this value a handler for something else?
#       if it's handler something that's deferred, will need to change marked as well
def correct_observed(obj, name, new_value):
    if hasattr(obj, name) and callable(getattr(obj, name)) and \
        (is_handler(getattr(obj, name)) or is_handler(getattr(obj, name).__func__)):
        candidate = getattr(obj, name)
        if isinstance(candidate, ObservableFunction):
            candidate = candidate.__func__
        new_value.__func__._observing = candidate._observing
        for attempted_observable in candidate._observing:
            mode = candidate._observing[attempted_observable]["mode"]
            name = candidate._observing[attempted_observable]["name"]
            if mode == "deferred":
                obj.marked[attempted_observable][name].remove(getattr(obj, name))
                obj.marked[attempted_observable][name].add(new_value)
            else:
                attempted_observable.deregister_handler(getattr(obj, name))
                attempted_observable.deregister_handler(new_value)

#   who are the handlers of this value?
def correct_handlers(obj, name, new_value):
    has_handlers = name in obj.marked[name] and len(obj.marked[name][name]) > 0
    if has_handlers:
        for handler in obj.marked[name][name]:
            if isinstance(handler, ObservableFunction):
                observing = handler.__func__.observing
            else:
                observing = handler._observing

            candidate = name
            if hasattr(obj, name):
                candidate = object.__getattribute__(obj, name)

            observing[new_value] = observing[candidate]
            del observing[candidate]

            new_value.register_handler(handler)


class ContainsObservables(object):
    def _oget(self, n):
        return super().__getattribute__(n)

    def _oset(self, n, v):
        super().__setattr__(n, v)

    def __delattr__(self, n):
        if n in self.marked and hasattr(self, n):
            # TODO: properly ignore
            pass
        object.__delattr__(self, n)

    def __getattribute__(self, n):
        if isinstance(super().__getattribute__(n), ObservableValue):
            return object.__getattribute__(self, n).get()
        else:
            return object.__getattribute__(self, n)

    # TODO: clean this up
    def __setattr__(self, n, v):
        new_v = v

        # goal is to properly reconstruct observable chain if attrib is in marked
        # at this point, all observables are set up...
        if n in self.marked:

            # set up new value
            has_handlers = n in self.marked[n] and len(self.marked[n][n]) > 0
            if has_handlers:
                new_v = create_observable_from_value(v)

            # need to recursively set up marked


            # two directions to think about here...

            #   is this value a handler for something else?
            #       if it's handler something that's deferred, will need to change marked as well
            correct_observed(self, n, new_v)


            #   who are the handlers of this value?
            correct_handlers(self, n, new_v)


        super().__setattr__(n, new_v)


        if hasattr(self, n) and isinstance(super().__getattribute__(n), ObservableValue):
            # pass
            super().__getattribute__(n).set(v)
        elif n not in self.marked:
            return super().__setattr__(n, v)


class Observable(object):
    def __init__(self):
        self._handlers = set()

    def register_handler(self, f):
        self._handlers.add(f)

    def deregister_handler(self, f):
        self._handlers.remove(f)

class ObservableFunction(Observable):
    def __init__(self, f):
        super().__init__()
        self.__func__ = f
        self._old_ret = None

        # for all the observables this is observing, change reference to self
        if is_handler(self.__func__):
            for observee in self.__func__._observing:
                if self.__func__._observing[observee]["mode"] != "deferred":
                    observee._handlers.remove(self.__func__)
                    observee._handlers.add(self)

    def __call__(self, *args, **kwargs):
        returned_value = self.__func__(*args, **kwargs)
        # print(self._handlers)
        # invoke _handlers
        for handler in self._handlers:

            f = handler
            if is_bound_method(f) or isinstance(handler, Observable):
                f = handler.__func__
            n = f._observing[self]["name"]

            handler(new={"name": n, "value": returned_value},
                old={"name": n, "value":  self._old_ret})

        self._old_ret = returned_value


class ObservableValue(Observable):
    def __init__(self, value):
        super().__init__()
        self.__value = value
        self._old_value = None

    def get(self):
        return self.__value

    def set(self, value):
        self._old_value = self.__value
        self.__value = value

        # invoke _handlers
        for handler in self._handlers:

            f = handler
            if is_bound_method(f) or isinstance(handler, Observable):
                f = handler.__func__
            n = f._observing[self]["name"]

            handler(new={"name": n, "value": self.__value},
                old={"name": n, "value": self._old_value})
