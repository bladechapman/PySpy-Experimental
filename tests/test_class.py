from pyspy import ObservableValue, ObservableFunction
from pyspy import observe, ignore, setup
import unittest

class TestClassUsage(unittest.TestCase):

    def test_direct_value(self):
        test_self = self

        class Test(object):
            @setup
            def __init__(self):
                self.value = 3
                self.handler_called = False

            @observe("value", is_class=True)
            def handler(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "value")
                test_self.assertEqual(old["name"], "value")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], 3)
                self.handler_called = True

        t = Test()
        t.value.set(4)
        self.assertEqual(t.handler_called, True)

    def test_direct_function(self):
        test_self = self

        class Test(object):
            @setup
            def __init__(self):
                self.handler_called = False

            def value(self):
                self.handler_called = True
                return 4

            @observe("value", is_class=True)
            def handler(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "value")
                test_self.assertEqual(old["name"], "value")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], None)
                self.handler_called = True

        t = Test()
        t.value()
        self.assertEqual(t.handler_called, True)

    def test_chained_value(self):
        test_self = self

        class Test(object):
            @setup
            def __init__(self):
                self.value = 3
                self.handler1_called = False
                self.handler2_called = False

            @observe("value", is_class=True)
            def handler1(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "value")
                test_self.assertEqual(old["name"], "value")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], 3)
                self.handler1_called = True
                return new["value"]

            @observe("handler1", is_class=True)
            def handler2(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "handler1")
                test_self.assertEqual(old["name"], "handler1")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], None)
                self.handler2_called = True

        t = Test()
        t.value.set(4)
        self.assertEqual(t.handler1_called, True)
        self.assertEqual(t.handler2_called, True)

    def test_chained_function(self):
        test_self = self

        class Test(object):
            @setup
            def __init__(self):
                self.handler1_called = False
                self.handler2_called = False

            def value(self, v):
                return v

            @observe("value", is_class=True)
            def handler1(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "value")
                test_self.assertEqual(old["name"], "value")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], None)
                self.handler1_called = True
                return new["value"]

            @observe("handler1", is_class=True)
            def handler2(self, new=None, old=None):
                nonlocal test_self
                test_self.assertEqual(new["name"], "handler1")
                test_self.assertEqual(old["name"], "handler1")

                test_self.assertEqual(new["value"], 4)
                test_self.assertEqual(old["value"], None)
                self.handler2_called = True

        t = Test()
        t.value(4)
        self.assertEqual(t.handler1_called, True)
        self.assertEqual(t.handler2_called, True)

    def test_lazy_observe_ignore(self):

        class Test1(object):
            @setup
            def __init__(self):
                self.value = None
                self.test2_being_observed = False
                self.handler_fired = False

            @observe("value", is_class=True)
            def handle_assignment(self, new=None, old=None):
                if new["value"] is not None:
                    new["value"].value2 = ObservableValue(new["value"].value2)
                    observe(new["value"].value2)(self.handler)
                    self.test2_being_observed = True
                else:
                    ignore(old["value"].value2)(self.handler)
                    old["value"].value2 = old["value"].value2.get()
                    self.test2_being_observed = False

            def handler(self, new=None, old=None):
                self.handler_fired = True

        class Test2(object):
            def __init__(self):
                self.value2 = 3

        t = Test1()
        t.value.set(Test2())
        t.value.get().value2.set(4)
        self.assertTrue(t.test2_being_observed)
        self.assertTrue(t.handler_fired)
        t.value.set(None)
        self.assertFalse(t.test2_being_observed)

if __name__ == "__main__":
    unittest.main()
