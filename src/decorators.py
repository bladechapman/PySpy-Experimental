from functools import wraps
import inspect
import operator
from .helpers import *
from .types import *

def observe(observable, is_class=False, name=None):
    def wrap(handler):
        if not isinstance(observable, Observable) and is_class == False:
            raise TypeError("Given observable must be instance of Observable if not used in class")
        elif not isinstance(observable, str) and is_class == True:
            raise TypeError("Observable must be string reference if used in class")

        # retrieve the underlying function
        f = handler
        while hasattr(f, "__func__"):
            f = getattr(f, "__func__")

        # if not handler, promote
        if not is_handler(f):
            f._observing = dict()

        # build link, no double registering
        f._observing[observable] = {"type": "reference" if isinstance(observable, Observable) else "string", \
            "name": name if name is not None else observable}
        # in the case of classes, this might be a string, so observables
        # are registered at init time
        if isinstance(observable, Observable):
            observable.register_handler(handler)

        return handler
    return wrap

def ignore(observable):
    def wrap(handler):
        if not isinstance(observable, Observable):
            raise TypeError("Given observable must be instance of Observable")

        # retrive the underlying function
        f = handler
        while hasattr(f, "__func__"):
            f = getattr(f, "__func__")

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
                top_sort(h, observed_ordering, 1, observed)
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
