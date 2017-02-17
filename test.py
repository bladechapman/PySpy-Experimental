#!/usr/bin/env python3

import unittest
# from tests.test_basic import TestBasicUsage
# from tests.test_class import TestClassUsage

from pyspy import *

class TestPrototype(unittest.TestCase):

    def test_prototype(self):


        # atm defered means nonexistent at init time


        class Test1(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()
                # self.value = 13

            # @observe("value1.value2.value3", is_class=True, deferred=True)
            # def handler123(self, old=None, new=None):
            #     print("HANDLER123")
            #
            # @observe("value1.value2", is_class=True, deferred=True)
            # def handler12(self, old=None, new=None):
            #     print("HANDLER12")
            #
            # @observe("value1", is_class=True, deferred=True)
            # def handler1(self, old=None, new=None):
            #     print("HANDLER1")



            # @observe("value1", is_class=True, deferred=True)
            @observe("value", is_class=True, deferred=True)
            def handler(self, old=None, new=None):
                print("HANDLER")

            @observe("handler", is_class=True, deferred=False)
            def handler_handler(self, old=None, new=None):
                print("HANDLERHANDLER")

            @observe("handler_handler", is_class=True, deferred=False)
            def handler_handler_handler(self, old=None, new=None):
                print("HANDLERHANDLERHANDLER")

            @observe("handler_handler_handler", is_class=True, deferred=False)
            def handler_handler_handler_handler(self, old=None, new=None):
                print("HANDLERHANDLERHANDLERHANDLER")



        class Test2(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()
                self.value2 = Test3()

        class Test3(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()
                self.value3 = 3


        t = Test1()
        # t.value1 = Test2()
        # print("---")
        # t.value1.value2 = Test3()
        # print("----")
        # t.value1.value2.value3 = "ABC"
        t.value = 12345
        # print(t.handler_handler._handlers)z


        # print(object.__getattribute__(t, "value"))
        # print(t._oget("value"))
        # t.value = 12345
        # t.handler()

        # def test_func(s, old=None, new=None):
        #     print("ABC123")
        # t.value = test_func
        # t.value(1, 2, 3)

        # print(t.marked)

        # t.value1.value2 = Test3()
        # t.value1.value2.value3 = 4

        # print(t.marked)
        # print(t.value1.marked)
        # print(t.value1.value2.marked)


        # print(t.marked)
        # print(t.value1.marked)
        # print(t.value1.value2.marked)

        # class Test2(ContainsObservables):
        #     @setup
        #     def __init__(self):
        #         super().__init__()
        #         self.value2 = Test3()
        #
        #
        # class Test3(ContainsObservables):
        #     @setup
        #     def __init__(self):
        #         super().__init__()
        #         self.value3 = Test4()
        #
        # class Test4(ContainsObservables):
        #     @setup
        #     def __init__(self):
        #         super().__init__()
        #         self.value4 = 8
        #
        #
        # class Test(ContainsObservables):
        #     @setup
        #     def __init__(self):
        #         super().__init__()
        #
        #         pass
        #
        #     @observe("value.value2", is_class=True, deferred=True)
        #     def handler3(self, old=None, new=None):
        #         print("HANDLED 3", new, old)
        #
        #     @observe("value.value2.value3.value4", is_class=True, deferred=True)
        #     def handler(self, old=None, new=None):
        #         # name seems to be incorrect
        #         # verify that old is value is correct
        #         print("HANDLED", new, old)
        #
        #     # # this gets double triggered...
        #     # @observe("value4", is_class=True, deferred=True)
        #     # def handler2(self, old=None, new=None):
        #     #     print("HANDLED 2", new, old)
        #
        #     # # watch for situations where marked gets overridden...
        #     # @observe("value", is_class=True, deferred=True)
        #     # def handler2(self, old=None, new=None):
        #     #     print("HANDLED 2", new, old)
        #
        #
        #
        #
        # t = Test()
        # t.value = Test2()
        #
        # print(t.marked)
        #
        # # t.value.value2 = Test3()
        #
        # # TODO: get rid of this
        # # t.value.value2.value3 = 18
        #
        # # t.value.value2 = Test3()
        # # t.value.value2.value3 = 19
        #
        #
        # # t.value4 = 20
        #
        # # del t.value
        # # t.value = 5

unittest.main()
