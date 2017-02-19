from functools import wraps, reduce
import inspect
import operator
from .helpers import *
from .types import *

def observe(observable, is_class=False, name=None, deferred=True):
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
        f._observing[observable] = { \
            "mode": \
                "reference" if isinstance(observable, Observable) else
                "string" if deferred == False else \
                "deferred", \
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
        # indicate that object is part of an observables chain
        add_marked(self)

        # run the original init function
        init_func(self, *args, **kwargs)


        # gather information about what's being observed
        observed_to_handlers, observed_modes = gather_obj_observations(self)


        # construct initialization order for undeferred observed
        root_observed_to_handlers = gather_root_observed(self, observed_to_handlers, observed_modes)
        ordering = build_ordering_for_root_observed(observed_to_handlers)
        ordering = [i for i in ordering if observed_modes[i[0]] != "deferred"]



        # initialize observables in order
        # also correct references to observables in handlers
        for observed_name, order in ordering:
            original = chained_getattr(self, observed_name)
            v = chained_getattr(self, observed_name)

            # create the observable
            # reference fixing is done automatically during initialization of observables
            if not isinstance(v, Observable):
                if callable(v):
                    v = ObservableFunction(v)
                else:
                    v = ObservableValue(v)
                chained_setattr(self, observed_name, v)

            # fix the reference to the observable in the handlers, register
            for handler in observed_to_handlers[observed_name]:
                original_ref = handler._observing[observed_name]
                del handler._observing[observed_name]
                handler._observing[v] = {"mode": "reference", "name": original_ref["name"]}
                v.register_handler(handler)


            # fix ref in observed_to_handlers, needed for setting up marked
            if isinstance(v, ObservableFunction):
                if is_handler(v.__func__):
                    for key in v.__func__._observing:
                        observing_name = v.__func__._observing[key]["name"]
                        observed_to_handlers[observing_name].remove(v.__func__)
                        observed_to_handlers[observing_name].add(v)


            print("---")




        # set up marked, also handles nested marking, dependency order doesn't matter here
        for observed_name in observed_to_handlers:
            setup_marked(self, observed_name, observed_to_handlers[observed_name])
        print("--SETUP DONE--")

        # for observed_name, order in ordering:
        #     a = chained_getattr(self, observed_name)
        #
        #     # set observables
        #     v = chained_getattr(self, observed_name)
        #
        #     if not isinstance(v, Observable):
        #         if callable(a):
        #             v = ObservableFunction(a)
        #             chained_setattr(self, observed_name, v)
        #         else:
        #             v = ObservableValue(a)
        #             chained_setattr(self, observed_name, v)
        #
        #
        #     # fix references in observed for deferred setup
        #     if is_handler(a):
        #         for name in a._observing:
        #             observed_to_handlers[name].remove(a)
        #             observed_to_handlers[name].add(v)
        # for observed_name, order in ordering:
        #     v = chained_getattr(self, observed_name, oget=True)
        #
        #     # correct and register handlers...
        #     for handler in observed_to_handlers[observed_name]:
        #         if isinstance(handler, ObservableFunction):
        #             handler_real = handler.__func__
        #         else:
        #             handler_real = handler
        #
        #         n = handler_real._observing[observed_name]["name"]
        #         del handler_real._observing[observed_name]
        #         handler_real._observing[v] = {"mode": "reference", "name": n}
        #         v.register_handler(handler)


        # mark both deferred and undeferred observables


    return modified_init_func



# def setup(init_func):
#     @wraps(init_func)
#     def modified_init_func(self, *args, **kwargs):
#         # call original init to set up class
#         object.__setattr__(self, "marked", dict())
#         object.__setattr__(self, "setup", dict())
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
#         # gather observed attributes
#         observed = dict()
#         observed_type = dict()
#         for n, h in unmodified_handler_functions:
#             for t in h._observing:
#                 if t not in observed:
#                     observed[t] = set()
#                 observed[t].add(h)
#                 observed_type[t] = h._observing[t]["mode"]
#
#
#
#
#
#         observed_functions = {i:observed[i] for i in observed if observed_type[i] != "deferred" and callable(chained_getattr(self, i))}
#         observed_attributes = {i:observed[i] for i in observed if observed_type[i] != "deferred" and not callable(chained_getattr(self, i))}
#         root_observed_functions = {}
#         for func_name in observed_functions:
#             should_add = False
#             if is_handler(chained_getattr(self, func_name)):
#                 observing = chained_getattr(self, func_name)._observing
#                 statuses = map(lambda x: observing[x]["mode"] == "deferred", observing)
#                 should_add = reduce(lambda x, y: x or y, statuses, True)
#             else:
#                 should_add = True
#
#             if should_add:
#                 root_observed_functions[func_name] = observed_functions[func_name]
#         root_observed = {i:observed[i] for i in observed if i in root_observed_functions or i in observed_attributes}
#
#         # topological sort from root nodes
#         observed_ordering = {i:0 for i in observed if observed_type[i] != "deferred"}
#         for i in root_observed:
#             for h in observed[i]:
#                 top_sort(h, observed_ordering, 1, observed)
#         ordering = sorted(observed_ordering.items(), key=operator.itemgetter(1))
#
#
#         # print(ordering)
#
#
#         # initialize observables in order
#         for observed_name, order in ordering:
#
#             a = chained_getattr(self, observed_name)
#
#             # set observables
#             v = chained_getattr(self, observed_name)
#
#             if not isinstance(v, Observable):
#                 if callable(a):
#                     v = ObservableFunction(a)
#                     chained_setattr(self, observed_name, v)
#                 else:
#                     v = ObservableValue(a)
#                     chained_setattr(self, observed_name, v)
#
#
#             # fix references in observed for deferred setup
#             if is_handler(a):
#                 for name in a._observing:
#                     observed[name].remove(a)
#                     observed[name].add(v)
#
#
#
#
#
#         for observed_name, order in ordering:
#             v = chained_getattr(self, observed_name, oget=True)
#
#             # correct and register handlers...
#             for handler in observed[observed_name]:
#                 if isinstance(handler, ObservableFunction):
#                     handler_real = handler.__func__
#                 else:
#                     handler_real = handler
#
#                 n = handler_real._observing[observed_name]["name"]
#                 del handler_real._observing[observed_name]
#                 handler_real._observing[v] = {"mode": "reference", "name": n}
#                 v.register_handler(handler)
#
#
#
#
#
#
#
#
#         # deferred / default observations
#         for observee in observed:
#             handlers = observed[observee]
#             # for handler in handlers:
#             #     print(handler.__func__)
#             # print(observee, handlers)
#             add_default_handler_for(observee, self, handlers)
#
#
#
#
#
#
#
#     return modified_init_func
