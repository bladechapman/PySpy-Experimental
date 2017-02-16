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
                print("HANDLED")


        t = Test()

        t.value = Test2()

        t.value.value2.value3 = 6
        # del t.value
        # t.value = 5

unittest.main()
