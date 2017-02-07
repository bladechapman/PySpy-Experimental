from functools import wraps
import inspect
import operator


#TODO: Clean up API
#TODO: Write tests
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

def observe(observable, is_class=False, name=None):
    def wrap(handler):
        if not isinstance(observable, Observable) and is_class == False:
            raise TypeError("Given observable must be instance of Observable if not used in class")
        elif not isinstance(observable, str) and is_class == True:
            raise TypeError("Observable must be string reference if used in class")

        # retrieve the underlying function
        f = None
        if isinstance(handler, ObservableFunction) or is_bound_method(handler):
            f = handler.__func__
        else:
            f = handler

        # if not handler, promote
        if not is_handler(f):
            f._observing = dict()

        # build link, no double registering
        f._observing[observable] = {"type": "reference" if isinstance(observable, Observable) else "string", \
            "name": name if name is not None else observable}
        if isinstance(observable, Observable):
            observable.register_handler(handler)

        return handler
    return wrap

def ignore(observable):
    def wrap(handler):
        if not isinstance(observable, Observable):
            raise TypeError("Given observable must be instance of Observable")

        # retrive the underlying function
        f = None
        if isinstance(handler, ObservableFunction):
            f = handler.__func__
        else:
            f = handler

        # provided handler must be a handler function
        if not is_handler(f):
            raise Exception("The provided handler is not actually a handler")

        # remove the handler from the observables it's observing
        # remove the observable from the handler's observing list
        for observing in f._observing:
            observing._handlers.remove(handler)
        del f._observing[observable]

        return handler
    return wrap

# TODO: GET RID OF THIS OR SOMETHING
def build_observed_ordering_for_root_node(node, ordering, init_val, observed):
    if node.__name__ not in observed:
        return

    if init_val > ordering[node.__name__]:
        ordering[node.__name__] = init_val

    for h in observed[node.__name__]:
        build_observed_ordering_for_root_node(h, ordering, init_val + 1, observed)

def setup(init_func):
    @wraps(init_func)
    def modified_init_func(self, *args, **kwargs):
        # call original init to set up class
        init_func(self, *args, **kwargs)


        # at this point the observed attributes have no link to their handlers
        #   1. convert these to observable versions
        # at this point the handlers only have string references to their targets
        #   2. change string references to actual references


        unmodified_handler_functions = [(i, j) for (i, j) \
            in inspect.getmembers(self, inspect.ismethod) \
            if is_handler(j)]

        # gather observed attributes
        observed = dict()
        for n, h in unmodified_handler_functions:
            for t in h._observing:
                if t not in observed:
                    observed[t] = []
                observed[t].append(h)
        observed_functions = {i:observed[i] for i in observed if callable(chained_getattr(self, i))}
        observed_attributes = {i:observed[i] for i in observed if not callable(chained_getattr(self, i))}
        root_observed_functions = {i:observed_functions[i] for i in observed_functions if not is_handler(chained_getattr(self, i))}
        root_observed = {i:observed[i] for i in observed if i in root_observed_functions or i in observed_attributes}


        # topological sort from root nodes
        observed_ordering = {i:0 for i in observed}
        for i in root_observed:
            for h in observed[i]:
                build_observed_ordering_for_root_node(h, observed_ordering, 1, observed)
        ordering = sorted(observed_ordering.items(), key=operator.itemgetter(1))


        # initialize observables in order
        for observed_name, order in ordering:
            a = chained_getattr(self, observed_name)

            # set observables
            v = chained_getattr(self, observed_name)
            if not isinstance(v, Observable):
                if callable(a):
                    v = ObservableFunction(a)
                    chained_setattr(self, observed_name, v)
                else:
                    v = ObservableValue(a)
                    chained_setattr(self, observed_name, v)

            # correct and register handlers...
            for handler in observed[observed_name]:
                n = handler._observing[observed_name]["name"]
                del handler._observing[observed_name]
                handler._observing[v] = {"type": "reference", "name": n}
                v.register_handler(handler)

    return modified_init_func




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
