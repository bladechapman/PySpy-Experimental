from pyspy import observe, PySpyBase

class Test2(PySpyBase):
    test_val4 = 4

    def __init__(self):
        self.test_val3 = 3
        super().__init__()

    def __getattribute__(self, name):
        # print("GET:", name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        # print("SET:", name, value)
        return super().__setattr__(name, value)


class Test(PySpyBase):
    def __init__(self):

        self.test_val = 1
        self.test_val2 = 2
        self.chained_test = Test2()
        super().__init__()

    @observe("test_val")
    @observe("test_val2")
    @observe("chained_test.test_val3")
    @observe("chained_test.test_val4")
    def test(self):
        print("HANDLER:", \
            self.test_val, \
            self.test_val2,
            self.chained_test.test_val3,
            self.chained_test.test_val4)


t = Test()
t.test_val = 2
t.test_val2 = 3
t.chained_test.test_val3 = 4
t.chained_test.test_val4 = 5
