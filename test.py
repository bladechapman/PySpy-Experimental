#!/usr/bin/env python3
from pyspy import observe, ignore, setup
from pyspy import ObservableValue, ObservableFunction, Observable


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
# t.set(4)
#
# handler = ignore(t)(handler)
# t.set(5)
#
# print("-----")
#
# class Test(object):
#
#     @setup
#     def __init__(self, t):
#         self.test = t
#
#     def test_fun2(self):
#         print("test_func2")
#
#     @observe("test_fun2", is_class=True)
#     def test_func3(self):
#         print("test_func3")
#
#     @observe("test", is_class=True)
#     def test_func(self):
#         print("test_func")
#
#     @observe("test_func", is_class=True)
#     def handler(self):
#         print("handler")
#
#
#
# t = Test(123)
# t.test.set(345)
# t.test_fun2()


# class Test2(object):
#     @setup
#     def __init__(self):
#         self.test2 = 123
#
#     @observe("test2", is_class=True)
#     def test3(self):
#         print("FDSAFAS")
#
#     @observe("test3", is_class=True)
#     def test4(self):
#         print("HDFSAFDS")
#
# class Test3(object):
#     @setup
#     def __init__(self):
#         self.test3 = Test2()
#
#     @observe("test3.test2", is_class=True)
#     def handler(self):
#         print("ASDFGHJKL")
#
#     @observe("test3.test4", is_class=True)
#     def handler2(self):
#         print("LFASGSA")
#
#
# t3 = Test3()
# t3.test3.test2.set(345)


class Test4(object):
    def __init__(self):
        self.test3 = 123

class Test5(object):
    @setup
    def __init__(self):
        self.test4 = None

    @observe("test4", is_class=True)
    def handler1(self):
        # TODO: investigate possibility of memory leak
        if self.test4.get() is not None:
            print("OBS")
            o = self.test4.get().test3
            self.test4.get().test3 = ObservableValue(self.test4.get().test3)
            observe(self.test4.get().test3)(self.handler2)

    def handler2(self):
        print("HANDLER2")

t5 = Test5()
t4 = Test4()
t5.test4.set(t4)
t4.test3.set(345)

t5.test4.set(None)

# need to clean up handler at some point, maybe pass as parameters?
t4.test3.set(567)
