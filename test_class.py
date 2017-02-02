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


if __name__ == "__main__":
    unittest.main()
