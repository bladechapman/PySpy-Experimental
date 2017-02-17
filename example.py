from uuid import uuid4
from pyspy import *
import threading
from random import random

def delay_random(lower=1.0, upper=3.0):
    """
    Decorator delaying the execution of a function
    http://fredericiana.com/2014/11/14/settimeout-python-delay/
    :param delay: the number of seconds to delay the function execution
    """
    def wrap(f):
        @wraps(f)
        def delayed(*args, **kwargs):
            delay = int(random() * upper + lower)
            timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
            timer.start()
        return delayed
    return wrap



class Foo(ContainsObservables):
    @setup
    def __init__(self):
        super().__init__()
        self.id = uuid4()
        self.name = "Foo!"
        self.value = int(random() * 100)
        self.change_val_random()

    @delay_random()
    def change_val_random(self):
        self.value = int(random() * 100)
        self.change_val_random()

    def serialize(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "value": self.value
        }


class Container(ContainsObservables):
    @setup
    def __init__(self):
        super().__init__()
        self.id = uuid4()
        self.foo1 = Foo()
        self.foo2 = Foo()
        self.foo3 = Foo()

    def serialize(self):
        return {
            "id": str(self.id),
            "foo1": self.foo1.serialize(),
            "foo2": self.foo2.serialize(),
            "foo3": self.foo3.serialize()
        }

    @observe("foo1.value", is_class=True, deferred=False)
    @observe("foo2.value", is_class=True, deferred=False)
    @observe("foo3.value", is_class=True, deferred=False)
    def handler(self, old=None, new=None):
        print(self.serialize())

t = Container()
