from .helpers import *

class ContainsObservables(object):
    def __init__(self):
        object.__setattr__(self, "marked", dict())

    def _oget(self, n):
        return super().__getattribute__(n)

    def _oset(self, n, v):
        super().__getattribute__(n, v)

    def __delattr__(self, n):
        if n in self.marked and hasattr(self, n):
            # TODO: ignore
            pass
        object.__delattr__(self, n)

    def __getattribute__(self, n):
        if isinstance(super().__getattribute__(n), ObservableValue):
            return object.__getattribute__(self, n).get()
        else:
            return object.__getattribute__(self, n)

    def __setattr__(self, n, v):
        if n in self.marked and not hasattr(self, n):
            # set up observable
            full_str, handlers = self.marked[n]

            if callable(v):
                o = ObservableFunction(v)
            else:
                o = ObservableValue(v)

            # TODO: verify that the naming is correct, especially for nested
            for handler in handlers:
                o.register_handler(handler)
                if n in handler._observing:
                    del handler._observing[n]
                handler._observing[o] = {"type": "reference", "name": n}

            object.__setattr__(self, n, o)


        if hasattr(self, n) and isinstance(super().__getattribute__(n), ObservableValue):
            super().__getattribute__(n).set(v)
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
                observee._handlers.remove(self.__func__)
                observee._handlers.add(self)

    def __call__(self, *args, **kwargs):
        returned_value = self.__func__(*args, **kwargs)

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
