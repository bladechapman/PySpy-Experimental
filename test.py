from pyspy import observe, ignore, Observable

class Test2(Observable):

    test_val4 = 4

    def __init__(self):
        self.test_val3 = 3
        Observable.reveal(self)

    def test_f4(self):
        print("INVOKED TEST_F4")
        return 4


class Test(Observable):
    def __init__(self):
        # self.chained_test = None
        self.chained_test = Test2()
        self.test_val = 3
        Observable.reveal(self)

    # @observe("chained_test")
    # @observe("test_val")
    def test_f1(self):
        pass
        # if self.chained_test is not None:
        #     observe("chained_test.test_val3")(self.test_f2)
        #     Observable.reveal(self)
        # else:
        #     ignore("chained_test.test_val3")(self.test_f2)
        #     Observable.reveal(self)

    @observe("chained_test.test_f4")
    @observe("chained_test.test_val3")
    @observe("test_f3")
    def test_f2(self, values):
        print("INVOKED TEST_F2", values)

    def test_f3(self):
        print("INVOKED TEST_F3")
        return 1


t1 = Test()

# print(t1.test_f2.__observed_attributes)

# print(t1.test_f3)
t1.test_f3()
# t1.chained_test.test_f4()

# t1.test_val = 45
# t1.chained_test.test_val3 = 321
