from pyspy import observe, PySpyBase
# from pyspy import setup

class Test(PySpyBase):
    def __init__(self):
        # pass
        self.test_val = 1
        self.test_val2 = 2
        self.unobserved = 10
        super().__init__()


    @observe("test_val")
    @observe("test_val2")
    def test(self):
        print("HANDLER:", self.test_val, self.test_val2, self.unobserved)
        # self.test_val2 = self.test_val2 + self.test_val

    # @observe("test_val2")
    # def test2(self):
    #     print(self.test_val2)


print("---INIT---")
t = Test()
print("---SET---")

t.test_val = 3
t.test_val2 = 5
