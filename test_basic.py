from pyspy import ObservableValue, ObservableFunction
from pyspy import observe, ignore
import unittest

class TestBasicUsage(unittest.TestCase):

    def test_direct_value(self):
        handler_triggered = False
        value = ObservableValue(2)

        def handler(new=None, old=None):
            nonlocal handler_triggered
            self.assertEqual(new["name"], value)
            self.assertEqual(old["name"], value)

            self.assertEqual(new["value"], 3)
            self.assertEqual(old["value"], 2)
            handler_triggered = True

        handler = observe(value)(handler)
        value.set(3)
        self.assertTrue(handler_triggered)

    def test_direct_function(self):
        handler_triggered = False
        def value():
            return True
        value = ObservableFunction(value)

        def handler(new=None, old=None):
            nonlocal handler_triggered
            self.assertEqual(new["name"], value)
            self.assertEqual(old["name"], value)

            self.assertEqual(new["value"], True)
            self.assertEqual(old["value"], None)
            handler_triggered = True

        handler = observe(value)(handler)
        value()
        self.assertTrue(handler_triggered)






        # value = ObservableFunction()
        #
        # def handler(new=None, old=None):
        #     print("HANDLE")
        #
        # handler = observe(value)(handler)

    def test_chained_value(self):
        handler1_triggered = False
        handler2_triggered = False
        value = ObservableValue(2)

        def handler1(new=None, old=None):
            nonlocal handler1_triggered
            self.assertEqual(new["name"], value)
            self.assertEqual(old["name"], value)

            self.assertEqual(new["value"], 3)
            self.assertEqual(old["value"], 2)
            handler1_triggered = True
            return True

        def handler2(new=None, old=None):
            nonlocal handler2_triggered
            self.assertEqual(new["name"], handler1)
            self.assertEqual(old["name"], handler1)

            self.assertEqual(new["value"], True)
            self.assertEqual(old["value"], None)
            handler2_triggered = True

        handler1 = observe(value)(handler1)
        handler1 = ObservableFunction(handler1)

        handler2 = observe(handler1)(handler2)

        value.set(3)
        self.assertTrue(handler1_triggered)
        self.assertTrue(handler2_triggered)

    def test_chained_function(self):
        handler1_triggered = False
        handler2_triggered = False
        def value():
            return 3
        value = ObservableFunction(value)

        def handler1(new=None, old=None):
            nonlocal handler1_triggered
            self.assertEqual(new["name"], value)
            self.assertEqual(old["name"], value)

            self.assertEqual(new["value"], 3)
            self.assertEqual(old["value"], None)
            handler1_triggered = True
            return True

        def handler2(new=None, old=None):
            nonlocal handler2_triggered
            self.assertEqual(new["name"], handler1)
            self.assertEqual(old["name"], handler1)

            self.assertEqual(new["value"], True)
            self.assertEqual(old["value"], None)
            handler2_triggered = True

        handler1 = observe(value)(handler1)
        handler1 = ObservableFunction(handler1)

        handler2 = observe(handler1)(handler2)

        value()
        self.assertTrue(handler1_triggered)
        self.assertTrue(handler2_triggered)

    def test_direct_value_ignore(self):
        value = ObservableValue(2)

        def handler(new=None, old=None):
            self.assertTrue(False)

        handler = observe(value)(handler)
        handler = ignore(value)(handler)
        value.set(3)

    def test_direct_function_ignore(self):
        def value():
            return True
        value = ObservableFunction(value)

        def handler(new=None, old=None):
            self.assertTrue(False)

        handler = observe(value)(handler)
        handler = ignore(value)(handler)
        value()

    def test_chained_value_ignore(self):
        value = ObservableValue(2)

        def handler1(new=None, old=None):
            self.assertTrue(new)
            self.assertFalse(old)
            return True

        def handler2(new=None, old=None):
            self.assertEqual(new["name"], handler1)
            self.assertEqual(old["name"], handler1)

            self.assertEqual(new["value"], True)
            self.assertEqual(old["value"], None)

        handler1 = observe(value)(handler1)
        handler1 = ObservableFunction(handler1)

        handler2 = observe(handler1)(handler2)
        handler1 = ignore(value)(handler1)

        value.set(3)
        handler1(new=True, old=False)


if __name__ == "__main__":
    unittest.main()
