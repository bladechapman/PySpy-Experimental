#!/usr/bin/env python3

import unittest
# from tests.test_basic import TestBasicUsage
# from tests.test_class import TestClassUsage

from pyspy import *

class TestPrototype(unittest.TestCase):

    def test_prototype(self):
        class Test(ContainsObservables):

            @setup
            def __init__(self):
                super().__init__()
                # self.value = 3

                pass

            @observe("value", is_class=True, deferred=True)
            def handler(self, old=None, new=None):
                print("HANDLED")

        t = Test()
        t.value = 4
        del t.value
        t.value = 5

unittest.main()
