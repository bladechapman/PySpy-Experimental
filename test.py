#!/usr/bin/env python3
from pyspy import observe, ignore, setup
from pyspy import ObservableValue, ObservableFunction


# t = ObservableValue(2)
#
# def handler():
#     print("HANDLED")
#
# handler = observe(t)(handler)
#
# def handler2():
#     print("HANDLED 2")
#
# handler = ObservableFunction(handler)
# handler2 = observe(handler)(handler2)
#
# def handler3():
#     print("HANDLED 3")
#
# handler2 = ObservableFunction(handler2)
# handler3 = observe(handler2)(handler3)
#
# print("---")
# t.set(4)
# print("---")
#
# handler = ignore(t)(handler)
# t.set(5)


class Test(object):

    @setup
    def __init__(self, t):
        self.test = t

    @observe("test", is_class=True)
    def test_func(self):
        print("test_func")

    @observe("test_func", is_class=True)
    def handler(self):
        print("handler")




print("---")
t = Test(123)
# t.test_func()

# t.test.set(345)
