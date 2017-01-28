from functools import wraps
import inspect
import gc
import operator

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

def observe(observable, is_class=False):
    def wrap(handler):
        if not isinstance(observable, Observable) and is_class == False:
            raise TypeError("Given observable must be instance of Observable if not used in class")
        elif not isinstance(observable, str) and is_class == True:
            raise TypeError("Observable must be string reference if used in class")

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
        f._observing[observable] = {"type": "reference" if isinstance(observable, Observable) else "string"}
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
        observed_functions = {i:observed[i] for i in observed if callable(getattr(self, i))}
        observed_attributes = {i:observed[i] for i in observed if not callable(getattr(self, i))}
        root_observed_functions = {i:observed_functions[i] for i in observed_functions if not is_handler(getattr(self, i))}
        root_observed = {i:observed[i] for i in observed if i in root_observed_functions or i in observed_attributes}

        # print(observed_attributes)
        # print(root_observed_functions)
        # print(root_observed)


        # topological sort from root nodes
        observed_ordering = {i:0 for i in observed}
        for i in root_observed:
            if not callable(getattr(self, i)):
                # setattr(self, i, ObservableValue(getattr(self, i)))
                pass
            for h in observed[i]:
                # setattr(self, i, ObservableValue(getattr(self, i)))
                build_observed_ordering_for_root_node(h, observed_ordering, 1, observed)
        # print(observed_ordering)

        ordering = sorted(observed_ordering.items(), key=operator.itemgetter(1))


        # initialize observables in order
        for observed_name, order in ordering:
            a = getattr(self, observed_name)
            # print(a)

            # register handlers...
            # print(observed_name)
            v = None
            if callable(a):
                v = ObservableFunction(a)
                setattr(self, observed_name, v)
                # for handler in observed[observed_name]:
                #     del handler._observing[observed_name]
                #     handler._observing[v] = {"type": "reference"}
                #     v.register_handler(handler)
            else:
                v = ObservableValue(a)
                setattr(self, observed_name, v)
                # for handler in observed[observed_name]:
                #     del handler._observing[observed_name]
                #     handler._observing[v] = {"type": "reference"}
                #     v.register_handler(handler)

            for handler in observed[observed_name]:
                del handler._observing[observed_name]
                handler._observing[v] = {"type": "reference"}
                v.register_handler(handler)


                    # print(handler._observing)
                # print(observed[observed_name])


            # val = 1
            # for h in handlers:
            #     h_name = h.__name__
            #     observed_ordering[h_name] = val
            #
            #     print(h_name)
                # print(observed_attributes[i])

            # for h_name in root_observed[i]:
                # print(h_name)
                # h = getattr(self, h_name)
                # print(h)
                # print(h._observing)

            # print(root_observed[i])
            # # v = 1
            # while root_observed[i]




        # print(getattr(self, 'test_func')._observing)

        # # replace attributes first, since they can't be observing anything
        # for a_s in observed_attributes:
        #     a = getattr(self, a_s)
        #     o_a = ObservableValue(a)
        #     setattr(self, a_s, o_a)
        #
        #     # change string references to this observed attribute to actual references
        #     for h in observed_attributes[a_s]:
        #         del h._observing[a_s]
        #         h._observing[o_a] = {"type": "reference"}
        #         o_a.register_handler(h)
        #
        # # topological sort based on distance from root observable?


        # # TODO
        # # convert observed_attributes
        # for a_s in observed_attributes:
        #     # TODO: Change this to chained getattr
        #     a = getattr(self, a_s)
        #
        #     o_a = None
        #     if callable(a):
        #         # TODO: Check to see how this works w/ bound functions
        #         # error occurs when a is handler and a._observing still contais string references...
        #         o_a = ObservableFunction(a) # a needs to be
        #     else:
        #         o_a = ObservableValue(a)
        #
        #     # replace normal attribute w/ observable version
        #     setattr(self, a_s, o_a)
        #
        #     # change string references to actual references
        #     for h in observed_attributes[a_s]:
        #         del h._observing[a_s]
        #         o_a.register_handler(h)
        #         h._observing[o_a] = {"type": "reference"}


    return modified_init_func


class Observable(object):
    def __init__(self):
        self._handlers = set()

    def register_handler(self, f):
        self._handlers.add(f)


# TODO: Handle arguments, bound functions
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
