#!/usr/bin/env python3
# from pyspy import observe, ignore, setup
# from pyspy import ObservableValue, ObservableFunction, Observable

# from test_basic import TestBasicUsage
#
# import unittest
# unittest.main()

#
# class Test(object):
#
#     @setup
#     def __init__(self, t):
#         self.test = t
#
#     # def test_fun2(self):
#     #     print("test_func2")
#     #
#     # @observe("test_fun2", is_class=True)
#     # def test_func3(self):
#     #     print("test_func3")
#
#     @observe("test", is_class=True)
#     def test_func(self, new_val=None, old_val=None):
#         print(new_val, old_val)
#         print("test_func")
#
#     # @observe("test_func", is_class=True)
#     # def handler(self):
#     #     print("handler")
#
#
#
# t = Test(123)
# t.test.set(345)
# # t.test_fun2()
#
#
# class Test2(object):
#     @setup
#     def __init__(self):
#         self.test2 = 123
#
#     @observe("test2", is_class=True)
#     def test3(self, new_val=None, old_val=None):
#         print("FDSAFAS")
#         print(new_val, old_val)
#
#     @observe("test3", is_class=True)
#     def test4(self, new_val=None, old_val=None):
#         print("HDFSAFDS")
#
# class Test3(object):
#     @setup
#     def __init__(self):
#         self.test3 = Test2()
#
#     @observe("test3.test2", is_class=True)
#     def handler(self, new_val=None, old_val=None):
#         print("ASDFGHJKL")
#         print(new_val, old_val)
#
#     @observe("test3.test4", is_class=True)
#     def handler2(self, new_val=None, old_val=None):
#         print("LFASGSA")
#
#
# t3 = Test3()
# t3.test3.test2.set(345)
#
#
# class Test4(object):
#     def __init__(self):
#         self.test3 = 123
#
# class Test5(object):
#     @setup
#     def __init__(self):
#         self.test4 = None
#
#     @observe("test4", is_class=True)
#     def handler1(self, new_val=None, old_val=None):
#         # TODO: investigate possibility of memory leak
#         if self.test4.get() is not None:
#             print("OBS")
#             o = self.test4.get().test3
#             self.test4.get().test3 = ObservableValue(self.test4.get().test3)
#             observe(self.test4.get().test3)(self.handler2)
#         else:
#             print("IGN")
#             o = old_val["value"].test3
#             ignore(old_val["value"].test3)(self.handler2)
#             # print(old_val["value"].)
#
#     def handler2(self, new_val=None, old_val=None):
#         print("HANDLER2")
#
# t5 = Test5()
# t4 = Test4()
# t5.test4.set(t4)
# t4.test3.set(345)
# t5.test4.set(None)
# t4.test3.set(567)


# class Test6(object):
#     @setup
#     def __init__(self):
#         self.test_val = 123
#         self.test_val2 = "ABC"
#
#     @observe("test_val", is_class=True)
#     @observe("test_val2", is_class=True)
#     def handler(self, old_val=None, new_val=None):
#         print("HANDLING")
#         print(new_val, old_val)
#         return new_val["value"]
#
#     @observe("handler", is_class=True)
#     def handler2(self, old_val=None, new_val=None):
#         print("HANDLING2")
#         print(new_val, old_val)
#
# t = Test6()
# t.test_val.set(345)
