#!/usr/bin/env python3

import unittest
# from tests.test_basic import TestBasicUsage
# from tests.test_class import TestClassUsage

from pyspy import *

class TestPrototype(unittest.TestCase):
    def test_nested(self):
        class Test2(ContainsObservables):
            @setup
            def __init__(self):
                self.value2 = 3

        class Test(ContainsObservables):
            @setup
            def __init__(self):
                self.value1 = Test2()

            @observe("value1.value2", is_class=True, deferred=False)
            def handler(self, old=None, new=None):
                print("HANDLE")

        t = Test()
        print(t.marked)
        print(t.value1.marked)
        # print("----")
        t.value1 = Test2()
        print(t.marked)
        print(t.value1.marked)
        #
        #
        #
        # t.value1.value2 = 5

        # print(object.__getattribute__(t.value1, "value2"))

    def _test_direct_value(self):
        test_self = self

        class Test(ContainsObservables):
            @setup
            def __init__(self):
                pass
                # self.value = 3

            @observe("value", is_class=True, deferred=True)
            def handler(self, new=None, old=None):
                print("HANDLE", new, old)

            @observe("handler", is_class=True, deferred=False)
            def handler2(self, new=None, old=None):
                print("HANDLE2", new, old)

            @observe("handler2", is_class=True, deferred=False)
            def handler3(self, new=None, old=None):
                print("HANDLE3", new, old)

        t = Test()
        print("---")

        t.value = 6


# class TestPrototype(unittest.TestCase):
#     def test_prototype(self):
#
#
#         class Test2(ContainsObservables):
#             def __init__(self):
#                 super().__init__()
#                 self.value2 = 3
#
#         class Test1(ContainsObservables):
#             @setup
#             def __init__(self):
#                 super().__init__()
#                 self.value = Test2()
#                 self.handler_fired = False
#
#             @observe("value.value2", is_class=True, deferred=False)
#             def handler(self, old=None, new=None):
#                 print("FDSAFAS", old, new)
#                 self.handler_fired = True
#
#         t = Test1()
#         print(t.marked)
#         print(t.value.marked)
#         t.value.value2 = 4


# class TestPrototype(unittest.TestCase):
#
#     def test_prototype(self):
#
#         class Test1(ContainsObservables):
#             @setup
#             def __init__(self):
#                 super().__init__()
#                 # self.value = 13
#
#             @observe("value1.value2.value3", is_class=True, deferred=True)
#             def handler123(self, old=None, new=None):
#                 print("HANDLER123", old, new)
#
#             @observe("handler12", is_class=True, deferred=False)
#             def handler12_2(self, old=None, new=None):
#                 print("HANDLER12_2", old, new)
#
#             @observe("value1.value2", is_class=True, deferred=True)
#             def handler12(self, old=None, new=None):
#                 print("HANDLER12", old, new)
#
#             @observe("value1", is_class=True, deferred=True)
#             def handler1(self, old=None, new=None):
#                 print("HANDLER1", old, new)
#
#
#
#             # @observe("value1", is_class=True, deferred=True)
#             @observe("value", is_class=True, deferred=True)
#             def handler(self, old=None, new=None):
#                 print("HANDLER", old, new)
#                 return new["value"]
#             #
#             @observe("handler", is_class=True, deferred=False)
#             def handler_handler(self, old=None, new=None):
#                 print("HANDLERHANDLER", old, new)
#                 return new["value"]
#
#             @observe("handler_handler", is_class=True, deferred=False)
#             def handler_handler_handler(self, old=None, new=None):
#                 print("HANDLERHANDLERHANDLER", old, new)
#                 return new["value"]
#             #
#             # @observe("handler_handler_handler", is_class=True, deferred=False)
#             # def handler_handler_handler_handler(self, old=None, new=None):
#             #     print("HANDLERHANDLERHANDLERHANDLER")
#
#
#
#         class Test2(ContainsObservables):
#             @setup
#             def __init__(self):
#                 super().__init__()
#                 self.value2 = Test3()
#
#         class Test3(ContainsObservables):
#             @setup
#             def __init__(self):
#                 super().__init__()
#                 self.value3 = 3
#
#
#         t = Test1()
#         t.value1 = Test2()
#         # t.value1.value2 = 123
#         # print("---")
#         # t.value1.value2 = Test3()
#         # print("----")
#         # t.value1.value2.value3 = "ABC"
#         # t.value = 12345
#         # print(t.handler_handler._handlers)


unittest.main()
