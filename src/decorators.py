from functools import wraps
import inspect
import operator
from .helpers import *
from .types import *


def observe(target, is_class=False, name=None, deferred=False):
    def wrap(handler):

        # # TODO: figure this out...
        # if deferred is True:
        #     return handler


        if not isinstance(target, Observable) and is_class == False:
            raise TypeError("Given target must be instance of Observable if not used in class")
        elif not isinstance(target, str) and is_class == True:
            raise TypeError("Target must be string reference if used in class")

        # retrieve the underlying function
        f = handler
        while hasattr(f, "__func__"):
            f = getattr(f, "__func__")

        # if not handler, promote
        if not is_handler(f):
            f._observing = dict()

        # build link, no double registering
        f._observing[target] = { \
            "mode": \
                "reference" if isinstance(target, Observable) else
                "string" if deferred == False else \
                "deferred",
            "name": name if name is not None else target}
        # in the case of classes, this might be a string, so targets
        # are registered at init time
        if isinstance(target, Observable):
            target.register_handler(handler)

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
        # call original func to set up class
        init_func(self, *args, **kwargs)

        # at this point the observed attributes have no link to their handlers
        #   1. convert these to observable versions
        # at this point the handlers only have string references to their targets
        #   2. change string references to actual references


        # gather strings of observed properties
        unmodified_handler_functions = [(i, j) for (i, j) \
            in inspect.getmembers(self, inspect.ismethod) \
            if is_handler(j)]
        # observed's string & info contained in handler._observing

        # set up observable chains for string observables
        #   the property may not be defined on the object yet
        #   at this point, register the appropriate handlers as well
        # probably need to top sort this
        for handler_name, handler_func in unmodified_handler_functions:
            for observed in handler_func._observing:
                observed_mode = handler_func._observing[observed]["mode"]


                print(handler_name)

                if observed_mode == "string":
                    o = create_observables_for_handler(handler_func, observed, self)

                    if o is not None:
                        n = handler_func._observing[observed]["name"]
                        del handler_func._observing[observed]
                        handler_func._observing[o] = {"mode": "reference", "name": n}




                    # observed_name.register_handler(handler_func)

                        #         #     for handler in observed_handlers[observed_name]:
                        #         #         n = handler._observing[observed_name]["name"]
                        #         #         del handler._observing[observed_name]
                        #         #         handler._observing[v] = {"type": "reference", "name": n}
                        #         #         v.register_handler(handler)




        # correct string references in handlers to actual references
        # for handler_name, handler_func in unmodified_handler_functions:
            # print(handler_func._observing)
            # for observed_name in handler_func._observing:
            #     print(observed_name)

    return modified_init_func


def create_observables_for_handler(handler, observed_name, obj):
    is_top_level = len(observed_name.split(".")) == 1
    current_elem = observed_name.split(".")[0]

    if not hasattr(obj, current_elem):
        if observed_name not in obj._marked:
            obj._marked[current_elem] = dict()
        obj._marked[current_elem][handler.__name__] = handler
        return None
    else:
        v = getattr(obj, current_elem)
        if not isinstance(v, Observable):
            v = ObservableFunction(v) if callable(v) else ObservableValue(v)
            v.register_handler(handler)
            setattr(obj, current_elem, v)
        return v


    # if not hasattr(obj, current_elem):
    #     obj._marked

    # pass


# def setup(init_func):
#     @wraps(init_func)
#     def modified_init_func(self, *args, **kwargs):
#         # call original init to set up class
#         init_func(self, *args, **kwargs)
#
#
#         # at this point the observed attributes have no link to their handlers
#         #   1. convert these to observable versions
#         # at this point the handlers only have string references to their targets
#         #   2. change string references to actual references
#
#         unmodified_handler_functions = [(i, j) for (i, j) \
#             in inspect.getmembers(self, inspect.ismethod) \
#             if is_handler(j)]
#
#
#         # gather observed attributes
#         observed_handlers = dict()
#         observed_types = dict()
#         for name, handler in unmodified_handler_functions:
#             for observee_name in handler._observing:
#                 if observee_name not in observed_handlers:
#                     observed_handlers[observee_name] = []
#                 observed_handlers[observee_name].append(handler)
#                 observed_types[observee_name] = handler._observing[observee_name]["type"]
#
#         # simply fitering by deferred is not the right way to do this
#         observed_functions = {i:observed_handlers[i] for i in observed_handlers \
#             if observed_types[i] != "deferred" and callable(getattr(self, i))}
#         observed_attributes = {i:observed_handlers[i] for i in observed_handlers \
#             if observed_types[i] != "deferred" and not callable(getattr(self, i))}
#
#         root_observed_functions = {i:observed_functions[i] for i in observed_functions \
#             if not is_handler(getattr(self, i))}
#         root_observed = {i:observed_handlers[i] for i in observed_handlers \
#             if i in root_observed_functions or i in observed_attributes}
#
#
#         # topological sort from root nodes
#         observed_ordering = {i:0 for i in observed_handlers}
#         for i in root_observed:
#             for h in observed_handlers[i]:
#                 top_sort(h, observed_ordering, 1, observed_handlers)
#         ordering = sorted(observed_ordering.items(), key=operator.itemgetter(1))
#
#
#         # # initialize top level bservables in order
#         # for observed_name, order in ordering:
#         #     # skip deferred, set up only top level observables
#         #     if observed_types[observed_name] == "deferred":
#         #         continue
#         #
#         #     # set observables
#         #     v = getattr(self, observed_name)
#         #     if not isinstance(v, Observable):
#         #         if callable(v):
#         #             v = ObservableFunction(v)
#         #             setattr(self, observed_name, v)
#         #         else:
#         #             v = ObservableValue(v)
#         #             setattr(self, observed_name, v)
#         #
#         #     # correct and register handlers...
#         #     for handler in observed_handlers[observed_name]:
#         #         n = handler._observing[observed_name]["name"]
#         #         del handler._observing[observed_name]
#         #         handler._observing[v] = {"type": "reference", "name": n}
#         #         v.register_handler(handler)
#
#
#
#         # # # handle deferred observables
#         # for observed_name, order in ordering:
#         #     for handler in observed_handlers[observed_name]:
#         #         create_observables_for_handler(handler, observed_name, self)
#         #
#         #         # create observables, register handler on observable
#         #         # correct handler's reference
#
#
#
#     return modified_init_func
