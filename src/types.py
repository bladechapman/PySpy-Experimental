from .helpers import *

# TODO: clean this up...
def setup_default_test(self, n, v, full_str, handlers):

    # print(n, v, handlers)

    if len(full_str.split(".")) != 1:
        if isinstance(v, ContainsObservables):
            add_default_handler_for(".".join(full_str.split(".")[1:]), v, handlers)

        if hasattr(v, full_str.split(".")[1]):
            setup_default_test(v, full_str.split(".")[1], getattr(v, full_str.split(".")[1]), ".".join(full_str.split(".")[1:]), handlers)

    # trigger handlers at root
    else:
        # set up observable
        if not isinstance(v, Observable):
            if callable(v):
                o = ObservableFunction(v)
            else:
                o = ObservableValue(v)
        else:
            o = v

        for handler in handlers:
            o.register_handler(handler)
            handler()



def add_default_handler_for(string, obj, handlers):
    components = string.split(".")
    if components[0] not in obj.marked:
        obj.marked[components[0]] = dict()

    obj.marked[components[0]][string] = handlers



    # if string == "handler":
    #     v = chained_getattr(obj, string)
    #     o = ObservableFunction(v)

    # try:
    #     v = chained_getattr(obj, string)
    #     # # set up observable
    #
    #     print(isinstance(v, Observable))
    #     print(callable(v))
    #     o= ObservableFunction(v)
    #
    #     # if not isinstance(v, Observable):
    #     #     if callable(v):
    #     #         o = ObservableFunction(v)
    #     #     else:
    #     #         o = ObservableValue(v)
    #     # else:
    #     #     o = v
    #     #
    #     # print(string, v)
    #     # print(o)
    #
    #
    # except AttributeError as e:
    #     print(e)
    # # try:
    # #     v = chained_getattr(obj, string)
    # #     if not isinstance(v, Observable):
    # #         if callable(v):
    # #             o = ObservableFunction(v)
    # #         else:
    # #             o = ObservableValue(v)
    # #     else:
    # #         o = v
    # # except Exception(e):
    # #     print(e)




class ContainsObservables(object):
    def __init__(self):
        # Two terrible names, one great price
        object.__setattr__(self, "marked", dict())
        object.__setattr__(self, "setup", dict())

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

    def __setattr__(self, n, v):

        if n in self.marked:
            for full_str in self.marked[n]:
                setup_default_test(self, n, v, full_str, self.marked[n][full_str])

        if hasattr(self, n) and isinstance(super().__getattribute__(n), ObservableValue):
            pass
            # super().__getattribute__(n).set(v)
        else:
            return super().__setattr__(n, v)


class Observable(object):
    def __init__(self):
        self._handlers = set()

    def register_handler(self, f):
        self._handlers.add(f)


class ObservableFunction(Observable):
    def __init__(self, f):
        super().__init__()
        self.__func__ = f
        self._old_ret = None

        if is_handler(self.__func__):
            for observee in self.__func__._observing:
                if not isinstance(observee, str):
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
