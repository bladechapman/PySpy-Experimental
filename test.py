from pyspy import observe, PySpyBase

class Test2():
    def __init__(self):
        self.test_val3 = 3

class Test(PySpyBase):
    def __init__(self):

        self.test_val = 1
        self.test_val2 = 2
        self.chained_test = Test2()
        super().__init__()

        # print(self.chained_test.test_val3)
        # print(getattr(self, "chained_test.test_val3"))
        print(getattr(getattr(self,"chained_test"), "test_val3"))

    @observe("test_val")
    @observe("test_val2")
    @observe("chained_test.test_val3")
    def test(self):
        print("HANDLER:", \
            self.test_val, \
            self.test_val2,
            self.chained_test.test_val3)


t = Test()
t.test_val = 3
t.test_val2 = 5
t.chained_test.test_val3 = 5
