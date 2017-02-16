#!/usr/bin/env python3

import unittest
# from tests.test_basic import TestBasicUsage
# from tests.test_class import TestClassUsage

from pyspy import *

class TestPrototype(unittest.TestCase):

    def test_prototype(self):

        class Test2(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()
                self.value2 = Test3()


        class Test3(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()
                self.value3 = 6


        class Test(ContainsObservables):
            @setup
            def __init__(self):
                super().__init__()

                pass

            @observe("value.value2.value3", is_class=True, deferred=True)
            def handler(self, old=None, new=None):
                # name seems to be incorrect
                # verify that old is value is correct
                print("HANDLED", new, old)

            @observe("value2", is_class=True, deferred=True)
            def handler2(self, old=None, new=None):
                print("HANDLED 2", new, old)


        t = Test()
        t.value = Test2()
        # TODO: get rid of this
        t.value.value2.value3 = 18

        t.value.value2 = Test3()
        t.value.value2.value3 = 19


        t.value2 = 20

        # del t.value
        # t.value = 5

unittest.main()
