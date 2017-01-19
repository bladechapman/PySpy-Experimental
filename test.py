from pyspy import observe, PySpyBase
# from pyspy import setup

class Test(PySpyBase):
    def __init__(self):
        super().__init__()
        self.test_val = 1
        self.test_val2 = 2
        self.unobserved = 3

    @observe("test_val")
    def test(self):
        self.test_val2 = self.test_val2 + self.test_val

    @observe("test_val2")
    def test2(self):
        print(self.test_val2)


print("---INIT---")
t = Test()
print("---SET---")
# t.test_val.__set__(10)
# t.test_val = 10
t.test_val = 4
